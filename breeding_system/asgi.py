"""
ASGI 入口 — HTTP + WebSocket 统一协议路由
=========================================

``ProtocolTypeRouter``：HTTP 走 Django ASGI 应用；WebSocket 走 Channels ``AuthMiddlewareStack``
与 ``apps.core.routing.websocket_urlpatterns``。

启动示例：``daphne -b 0.0.0.0 -p 8000 breeding_system.asgi:application``
"""

import os
from django.core.asgi import get_asgi_application

# 设置 Django 设置模块的环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'breeding_system.settings')

# 先初始化 Django ASGI 应用，确保所有应用（App）加载完成
# get_asgi_application() 内部会调用 django.setup()
django_asgi_app = get_asgi_application()

# 在初始化之后再导入 channels 及其它业务逻辑组件
# 关键：必须在 get_asgi_application() 之后导入，否则可能会触发 AppRegistryNotReady 异常
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.core import routing

# 定义协议路由器，处理不同类型的通信协议
application = ProtocolTypeRouter({
    # 标准 HTTP 协议
    "http": django_asgi_app,
    
    # WebSocket 协议
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns  # type: ignore
        )
    ),
})
