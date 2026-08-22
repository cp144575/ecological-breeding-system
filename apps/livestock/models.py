"""
牲畜域模型
==========

- ``LivestockCategory``：大类及可选 ``category_code``（用于批次号前缀）。
- ``LivestockArea``：养殖户下属栏舍/区域；删除时校验不在养批次。
- ``LivestockBatch``：核心业务批次；新建时 ``batch_code`` 由 ``_save_with_auto_batch_code`` 自动生成，
  出栏时触发溯源记录创建（见 ``save`` 方法与 ``traceability_app``）。
"""
import re

from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction
from django.utils import timezone
from typing import TYPE_CHECKING, Any
from apps.users.models import FarmerProfile

class LivestockCategory(models.Model):
    """
    牲畜大类表（模板表）
    """
    if TYPE_CHECKING:
        objects: Any
        livestockbatch_set: Any

    name = models.CharField(max_length=50, verbose_name="大类名称")
    category_code = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="分类代码")
    icon = models.ImageField(upload_to='category_icons/', null=True, blank=True, verbose_name="图标")
    standard_cycle = models.IntegerField(default=0, verbose_name="标准生长周期(天)", help_text="该大类品种从入栏到出栏的预计天数")  # type: ignore
    description = models.TextField(null=True, blank=True, verbose_name="描述")

    class Meta:
        db_table = 'livestock_category'
        verbose_name = '牲畜大类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class LivestockArea(models.Model):
    """
    养殖区域表
    """
    if TYPE_CHECKING:
        objects: Any
        livestockbatch_set: Any

    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='areas', verbose_name="所属养殖户")
    area_name = models.CharField(max_length=100, verbose_name="区域名称")
    image = models.ImageField(upload_to='areas/', null=True, blank=True, verbose_name="区域图片")
    description = models.TextField(null=True, blank=True, verbose_name="区域介绍")

    def delete(self, *args, **kwargs):
        """
        删除区域前校验：如果该区域还有在养批次，则禁止删除
        """
        if self.livestockbatch_set.filter(status='active').exists():
            from django.core.exceptions import ValidationError
            raise ValidationError("该区域内仍有在养牲畜，无法删除。请先完成出栏或转移。")
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'livestock_area'
        verbose_name = '养殖区域'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.area_name

class LivestockBatch(models.Model):
    """
    牲畜批次表
    """
    if TYPE_CHECKING:
        objects: Any
        vaccinations: Any
        diseases: Any
        category_id: Any
        farmer_id: Any
        area_id: Any

    STATUS_CHOICES = (
        ('active', '养殖中'),
        ('finished', '已出栏'),
        ('abnormal', '异常'),
    )
    category = models.ForeignKey(LivestockCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="牲畜分类")
    area = models.ForeignKey(LivestockArea, on_delete=models.PROTECT, null=True, verbose_name="养殖区域")
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='batches', verbose_name="所属养殖户")
    
    batch_code = models.CharField(max_length=50, unique=True, verbose_name="批次号")
    image = models.ImageField(upload_to='batches/', null=True, blank=True, verbose_name="牲畜图片")
    livestock_type = models.CharField(max_length=50, default="", verbose_name="牲畜种类")
    gender = models.CharField(max_length=20, default="混养", verbose_name="牲畜性别")
    breed = models.CharField(max_length=100, default="", verbose_name="牲畜品种")
    introduction = models.TextField(null=True, blank=True, verbose_name="牲畜简介")
    quantity = models.IntegerField(default=0, verbose_name="养殖数量")  # type: ignore
    entry_date = models.DateField(null=True, blank=True, verbose_name="入栏日期")
    finish_date = models.DateField(null=True, blank=True, verbose_name="出栏日期")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', db_index=True, verbose_name="状态")

    @property
    def eco_score(self):
        """
        计算生态评分 (1-5星)
        逻辑：
        1. 防疫记录覆盖 (基础 3 分)
        2. 疾病记录情况 (无疾病 +1 分，有疾病且已康复不扣分，未康复扣分)
        """
        score = 3.0
        
        # 1. 检查防疫记录
        if self.vaccinations.exists():
            score += 1.0
            
        # 2. 检查疾病记录
        diseases = self.diseases.all()
        if not diseases.exists():
            score += 1.0
        else:
            # 如果有未康复的疾病，扣分
            if diseases.exclude(status='recovered').exists():
                score -= 1.0
                
        return min(5.0, max(1.0, score))

    class Meta:
        db_table = 'livestock_batch'
        verbose_name = '牲畜批次'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.batch_code

    def _get_category_short_code(self) -> str:
        """
        获取牲畜大类短码。

        返回值：
            str：1-2 位的大类标识（字母/数字），用于批次号生成。
        """
        if not self.category_id:
            raise ValidationError('缺少牲畜大类，无法生成批次编号')

        raw_code = (getattr(self.category, 'category_code', None) or '').strip().upper()
        if not raw_code:
            name = (getattr(self.category, 'name', '') or '').strip()
            if '鸡' in name:
                raw_code = 'A'
            elif '鸭' in name:
                raw_code = 'B'
            elif '鹅' in name:
                raw_code = 'C'
            elif '羊' in name:
                raw_code = 'E'
            elif '牛' in name:
                raw_code = 'D'
            elif '猪' in name:
                raw_code = 'F'
            else:
                raw_code = 'U'

        normalized = re.sub(r'[^A-Z0-9]', '', raw_code)
        return (normalized or 'U')[:2]

    def _get_farmer_short_code(self) -> str:
        """
        获取养殖户短码。

        返回值：
            str：形如 F0001 的短码（基于 FarmerProfile.id 补零）。
        """
        if not self.farmer_id:
            raise ValidationError('缺少所属养殖户，无法生成批次编号')
        return f"F{int(self.farmer_id):04d}"

    def _get_entry_date_str(self) -> str:
        """
        获取批次日期字符串。

        返回值：
            str：YYYYMMDD 格式字符串。
        """
        date_val = timezone.now().date()
        return date_val.strftime('%Y%m%d')

    def _build_batch_code_prefix(self) -> str:
        """
        构建批次号前缀。

        返回值：
            str：{大类码}{YYYYMMDD}{养殖户短码}。
        """
        category_code = self._get_category_short_code()
        date_str = self._get_entry_date_str()
        farmer_short_code = self._get_farmer_short_code()
        return f"{category_code}{date_str}{farmer_short_code}"

    def _generate_next_batch_code(self) -> str:
        """
        生成下一条批次编号。

        返回值：
            str：完整批次编号，尾部包含当日同一养殖户同一大类的顺序号。
        """
        prefix = self._build_batch_code_prefix()
        last_code = (
            LivestockBatch.objects
            .filter(batch_code__startswith=prefix)
            .order_by('-batch_code')
            .values_list('batch_code', flat=True)
            .first()
        )
        last_seq = 0
        if last_code and len(last_code) > len(prefix):
            suffix = last_code[len(prefix):]
            if suffix.isdigit():
                last_seq = int(suffix)

        next_seq = last_seq + 1
        seq_width = max(3, len(str(next_seq)))
        return f"{prefix}{next_seq:0{seq_width}d}"

    def _save_with_auto_batch_code(self, *args, **kwargs):
        """
        创建批次时自动生成批次编号，并在冲突时重试。
        """
        if not self.area_id:
            raise ValidationError('缺少养殖区域，无法创建批次')

        max_attempts = 10
        for attempt_index in range(max_attempts):
            try:
                with transaction.atomic():
                    self.batch_code = self._generate_next_batch_code()
                    super().save(*args, **kwargs)
                return
            except IntegrityError as error:
                is_last_attempt = attempt_index >= max_attempts - 1
                if is_last_attempt:
                    raise error

    def save(self, *args, **kwargs):
        """
        保存批次数据。

        说明：
            1. 创建时强制由系统自动生成批次号（方案A）。
            2. 状态变为“已出栏”时自动生成溯源码。
        """
        is_new = self.pk is None
        old_status = None
        if not is_new:
            old_status = LivestockBatch.objects.get(pk=self.pk).status

        if is_new:
            self._save_with_auto_batch_code(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

        if self.status == 'finished' and (is_new or old_status != 'finished'):
            if not self.finish_date:
                self.finish_date = timezone.now().date()
                super().save(update_fields=['finish_date'])
            from apps.traceability_app.models import LivestockTrace
            trace_record, _created = LivestockTrace.objects.get_or_create(batch=self)
            if not trace_record.qr_code_image:
                trace_record.save()