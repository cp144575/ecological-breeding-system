"""
牲畜管理 REST 接口
==================

- ``LivestockCategoryViewSet``：大类（管理员可写，养殖户只读）；启动时可选补齐默认六畜。
- ``LivestockAreaViewSet``：养殖区域（养殖户 CRUD 自身）。
- ``LivestockBatchViewSet``：批次；创建时 ``batch_code`` 由模型自动生成。

详见各 ViewSet 类注释。
"""
from .models import LivestockCategory, LivestockArea, LivestockBatch
from apps.core.utils import BaseOwnerViewSet, BasePublicViewSet, DenyAll
from .serializers import (
    LivestockCategorySerializer, LivestockAreaSerializer, 
    LivestockBatchSerializer
)
from django.db import IntegrityError, transaction

class LivestockCategoryViewSet(BasePublicViewSet):
    """
    牲畜大类视图集 (管理员配置，养殖户仅读)
    """
    queryset = LivestockCategory.objects.all().order_by('id')
    serializer_class = LivestockCategorySerializer
    search_fields = ['name', 'category_code']

    def _ensure_default_categories(self):
        target_categories = [
            ('鸡', 'A', 45),
            ('鸭', 'B', 50),
            ('鹅', 'C', 80),
            ('牛', 'D', 540),
            ('羊', 'E', 180),
            ('猪', 'F', 180),
        ]

        with transaction.atomic():
            target_names = [name for name, _category_code, _standard_cycle in target_categories]
            existing_by_name = {
                (getattr(cat, 'name', '') or '').strip(): cat
                for cat in LivestockCategory.objects.select_for_update().filter(name__in=target_names)
            }
            used_codes = {
                (category_code or '').strip().upper()
                for category_code in (
                    LivestockCategory.objects.exclude(category_code__isnull=True)
                    .exclude(category_code='')
                    .values_list('category_code', flat=True)
                )
            }

            for name, category_code, standard_cycle in target_categories:
                normalized_code = (category_code or '').strip().upper()

                existing_category = existing_by_name.get(name)
                if existing_category is not None:
                    existing_code = (getattr(existing_category, 'category_code', None) or '').strip().upper()
                    existing_cycle = int(getattr(existing_category, 'standard_cycle', 0) or 0)

                    if not existing_code and normalized_code and normalized_code not in used_codes:
                        try:
                            existing_category.category_code = normalized_code
                            existing_category.save(update_fields=['category_code'])
                            used_codes.add(normalized_code)
                        except IntegrityError:
                            pass

                    if existing_cycle <= 0 and int(standard_cycle) > 0:
                        existing_category.standard_cycle = int(standard_cycle)
                        existing_category.save(update_fields=['standard_cycle'])
                    continue

                defaults = {
                    'standard_cycle': int(standard_cycle),
                    'description': None,
                }
                if normalized_code and normalized_code not in used_codes:
                    defaults['category_code'] = normalized_code

                try:
                    created_category, _created = LivestockCategory.objects.get_or_create(name=name, defaults=defaults)
                    created_code = (getattr(created_category, 'category_code', None) or '').strip().upper()
                    if created_code:
                        used_codes.add(created_code)
                except IntegrityError:
                    try:
                        LivestockCategory.objects.get_or_create(
                            name=name,
                            defaults={'standard_cycle': int(standard_cycle), 'description': None},
                        )
                    except IntegrityError:
                        continue

    def get_queryset(self):
        self._ensure_default_categories()
        return LivestockCategory.objects.filter(name__in=['鸡', '鸭', '鹅', '牛', '羊', '猪']).order_by('id')

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [DenyAll()]
        return super().get_permissions()

class LivestockAreaViewSet(BaseOwnerViewSet):
    """
    养殖区域视图集
    """
    queryset = LivestockArea.objects.all()
    serializer_class = LivestockAreaSerializer
    search_fields = ['area_name', 'description', 'farmer__farmer_name']
    select_related_fields = ['farmer']

class LivestockBatchViewSet(BaseOwnerViewSet):
    """
    牲畜批次视图集
    """
    queryset = LivestockBatch.objects.all()
    serializer_class = LivestockBatchSerializer
    search_fields = ['batch_code', 'category__name']
    filterset_fields = ['status', 'area', 'category']