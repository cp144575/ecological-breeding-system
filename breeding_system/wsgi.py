"""
WSGI 入口（同步 HTTP，不支持 WebSocket）
======================================

部署示例：Gunicorn ``gunicorn breeding_system.wsgi:application``。
若需同一进程承载 WebSocket，应使用 ASGI（``breeding_system.asgi``）配合 Daphne/Uvicorn。
"""

import os

from django.core.wsgi import get_wsgi_application

# 设置 Django 的设置模块路径
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'breeding_system.settings')

# 获取 WSGI 应用程序对象，供服务器（如 Gunicorn, Nginx）调用
application = get_wsgi_application()
