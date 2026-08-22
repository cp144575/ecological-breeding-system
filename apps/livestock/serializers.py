"""
牲畜序列化器
============

大类校验 ``category_code`` 与固定六畜映射；批次侧输出生长天数、进度、生态分、溯源字段等只读计算属性。
"""
from rest_framework import serializers
from .models import LivestockCategory, LivestockArea, LivestockBatch
from datetime import date
from apps.core.utils import get_image_upload_error

class LivestockCategorySerializer(serializers.ModelSerializer):
    """
    牲畜分类序列化器
    """

    allowed_category_code_by_name = {
        '鸡': 'A',
        '鸭': 'B',
        '鹅': 'C',
        '牛': 'D',
        '羊': 'E',
        '猪': 'F',
    }

    class Meta:
        model = LivestockCategory
        fields = '__all__'

    def validate_icon(self, value):
        error_msg = get_image_upload_error(value)
        if error_msg:
            raise serializers.ValidationError(error_msg)
        return value

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)

        if instance is None:
            name = (attrs.get('name') or '').strip()
            if name not in self.allowed_category_code_by_name:
                raise serializers.ValidationError({'name': '牲畜大类仅允许：鸡、鸭、鹅、牛、羊、猪'})

            expected_code = self.allowed_category_code_by_name[name]
            provided_code = attrs.get('category_code')
            if provided_code and str(provided_code).strip().upper() != expected_code:
                raise serializers.ValidationError({'category_code': f'该大类的大类码必须为 {expected_code}'})
            attrs['category_code'] = expected_code
            return attrs

        if 'name' in attrs and (attrs.get('name') or '').strip() != (instance.name or '').strip():
            raise serializers.ValidationError({'name': '不允许修改牲畜大类名称'})

        if 'category_code' in attrs and (attrs.get('category_code') or '').strip().upper() != (instance.category_code or '').strip().upper():
            raise serializers.ValidationError({'category_code': '不允许修改牲畜大类码'})

        return attrs

class LivestockAreaSerializer(serializers.ModelSerializer):
    """
    养殖区域序列化器
    """
    farmer_name = serializers.ReadOnlyField(source='farmer.farmer_name')

    class Meta:
        model = LivestockArea
        fields = '__all__'
        read_only_fields = ('farmer',)

    def validate_image(self, value):
        error_msg = get_image_upload_error(value)
        if error_msg:
            raise serializers.ValidationError(error_msg)
        return value

class LivestockBatchSerializer(serializers.ModelSerializer):
    """
    牲畜批次序列化器
    """
    category_name = serializers.ReadOnlyField(source='category.name')
    area_name = serializers.ReadOnlyField(source='area.area_name')
    farmer_name = serializers.ReadOnlyField(source='farmer.farmer_name')
    trace_code = serializers.ReadOnlyField(source='trace_record.trace_code')
    qr_code_image = serializers.ImageField(source='trace_record.qr_code_image', read_only=True)
    trace_url = serializers.SerializerMethodField()
    
    # 额外字段：生长天数、标准周期、生长进度、生态评分、预计出栏日期
    growth_days = serializers.SerializerMethodField()
    standard_cycle = serializers.ReadOnlyField(source='category.standard_cycle')
    growth_progress = serializers.SerializerMethodField()
    eco_score = serializers.SerializerMethodField()
    expected_finish_date = serializers.SerializerMethodField()

    class Meta:
        model = LivestockBatch
        fields = '__all__'
        read_only_fields = ('farmer', 'batch_code')

    def validate_image(self, value):
        error_msg = get_image_upload_error(value)
        if error_msg:
            raise serializers.ValidationError(error_msg)
        return value

    def get_growth_days(self, obj):
        """计算已养殖天数"""
        if not obj.entry_date:
            return 0
        
        # 如果已出栏，计算从入栏到出栏的天数
        end_date = obj.finish_date if obj.status == 'finished' and obj.finish_date else date.today()
        delta = end_date - obj.entry_date
        return max(0, delta.days)

    def validate_entry_date(self, value):
        if value and value > date.today():
            raise serializers.ValidationError('入栏日期不能晚于今天')
        return value

    def get_growth_progress(self, obj):
        """计算生长进度百分比"""
        if not obj.category or not obj.category.standard_cycle or not obj.entry_date:
            return 0
        
        growth_days = self.get_growth_days(obj)
        standard_cycle = obj.category.standard_cycle

        progress = round((growth_days / standard_cycle) * 100, 1)
        return min(100, max(0, progress))

    def get_eco_score(self, obj):
        """调用模型属性获取评分"""
        return obj.eco_score

    def get_expected_finish_date(self, obj):
        """计算预计出栏日期"""
        if not obj.entry_date or not obj.category or not obj.category.standard_cycle:
            return None
            
        from datetime import timedelta
        expected_date = obj.entry_date + timedelta(days=obj.category.standard_cycle)
        return expected_date

    def get_trace_url(self, obj):
        """
        功能：返回当前批次对应的公开溯源查询地址。

        参数：
            obj：当前批次对象

        返回值：
            str | None：公开溯源查询地址；若尚未生成溯源记录则返回 None
        """
        trace_record = getattr(obj, 'trace_record', None)
        if not trace_record:
            return None
        return trace_record.get_public_trace_url()