"""
溯源域模型 — ``LivestockTrace``
==============================

与 ``livestock.LivestockBatch`` 一对一；``trace_code`` 在首次保存时生成；
``rebuild_qr_code_image`` 使用 Python ``qrcode`` 库将公开溯源 URL 写成 ``qr_code_image`` 文件。

公开 URL 规则见 ``_build_public_trace_url``（支持 ``TRACE_PUBLIC_BASE_URL`` 与 DEBUG 下局域网前端端口）。
"""
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
import io
import socket
import uuid
from typing import TYPE_CHECKING, cast, Any

if TYPE_CHECKING:
    from django.db.models.manager import Manager
    from django.db.models.fields.files import ImageFieldFile
    from apps.livestock.models import LivestockBatch


def _get_local_ip() -> str:
    """
    功能：获取当前主机在局域网中的可访问 IP 地址。

    参数：
        无

    返回值：
        str：可用于局域网访问的 IPv4 地址；若获取失败则返回 127.0.0.1
    """
    socket_instance = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        socket_instance.connect(('8.8.8.8', 80))
        return socket_instance.getsockname()[0]
    except Exception:
        return '127.0.0.1'
    finally:
        socket_instance.close()


def _build_public_trace_url(trace_code: str) -> str:
    """
    功能：根据溯源码构建公开查询页面地址。

    参数：
        trace_code：溯源码字符串

    返回值：
        str：公开溯源查询页面完整地址或相对地址
    """
    base_url = (getattr(settings, 'TRACE_PUBLIC_BASE_URL', '') or '').strip().rstrip('/')
    if base_url:
        return f"{base_url}/public/trace/{trace_code}"

    if getattr(settings, 'DEBUG', False):
        return f"http://{_get_local_ip()}:5173/public/trace/{trace_code}"

    return f"/public/trace/{trace_code}"


class LivestockTrace(models.Model):
    """
    质量溯源模型 - 记录批次的出栏溯源信息
    """
    if TYPE_CHECKING:
        objects: 'Manager'

    batch = models.OneToOneField(
        'livestock.LivestockBatch', 
        on_delete=models.CASCADE, 
        related_name='trace_record',
        verbose_name="养殖批次"
    )
    trace_code = models.CharField(
        max_length=100, 
        unique=True, 
        db_index=True, 
        verbose_name="溯源码"
    )
    is_active = models.BooleanField(
        default=True,  # type: ignore
        verbose_name="是否启用"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="生成时间"
    )
    qr_code_image = models.ImageField(
        upload_to='trace_qr_codes/',
        null=True,
        blank=True,
        verbose_name="溯源二维码",
    )

    class Meta:
        verbose_name = "质量溯源"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        batch_instance = cast('LivestockBatch', self.batch)
        return f"{batch_instance.batch_code} - {self.trace_code}"

    def get_public_trace_url(self) -> str:
        """
        功能：获取当前溯源记录对应的公开查询地址。

        参数：
            无

        返回值：
            str：公开溯源查询页面地址
        """
        return _build_public_trace_url(cast(str, self.trace_code))

    def rebuild_qr_code_image(self, force: bool = False) -> bool:
        """
        功能：按当前公开访问地址重新生成二维码图片。

        参数：
            force：是否强制重建；为 True 时会覆盖已有二维码图片

        返回值：
            bool：生成成功返回 True，依赖缺失或生成失败返回 False
        """
        qr_code_image_file = cast('ImageFieldFile | None', self.qr_code_image)

        if qr_code_image_file and not force:
            return True

        if force and qr_code_image_file:
            # 修复静态类型误判：运行时这里是 ImageFieldFile，不是模型字段定义对象。
            current_qr_code_image = cast(Any, qr_code_image_file)
            current_qr_code_image.delete(save=False)
            self.qr_code_image = None

        try:
            import qrcode
            from qrcode.constants import ERROR_CORRECT_H
        except Exception:
            return False

        trace_url = self.get_public_trace_url()
        qr = qrcode.QRCode(
            error_correction=ERROR_CORRECT_H,
            box_size=10,
            border=2,
        )
        qr.add_data(trace_url)
        qr.make(fit=True)

        qr_image = cast(Any, qr.make_image(fill_color="black", back_color="white")).convert('RGB')
        buffer = io.BytesIO()
        qr_image.save(buffer, format='PNG')
        buffer.seek(0)

        file_name = f"trace_{self.trace_code}.png"
        # 修复静态类型误判：重新生成后实际持有的是文件对象，可直接调用 save。
        qr_code_image_field = cast(Any, self.qr_code_image)
        qr_code_image_field.save(file_name, ContentFile(buffer.getvalue()), save=False)
        super().save(update_fields=['qr_code_image'])
        return True

    def save(self, *args, **kwargs):
        """
        功能：保存溯源记录，并在首次保存后自动生成二维码图片。

        参数：
            *args：位置参数
            **kwargs：关键字参数

        返回值：
            无
        """
        if not self.trace_code:
            import time
            timestamp = int(time.time())
            self.trace_code = f"ECO{timestamp}{uuid.uuid4().hex[:6].upper()}"

        super().save(*args, **kwargs)

        if self.qr_code_image:
            return

        self.rebuild_qr_code_image(force=False)