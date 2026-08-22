"""
Channels WebSocket URL 列表（供 ``breeding_system.asgi`` 中 ``URLRouter`` 挂载）。

路径 ``ws/refresh/`` 与前端 ``websocket.ts`` 中构造的 URL 一致（开发态 often 指向 :8000）。
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/refresh/$', consumers.DataRefreshConsumer.as_asgi()),
]
