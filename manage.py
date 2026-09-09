#!/usr/bin/env python
"""
Django 命令行入口（``python manage.py <command>``）。

常用命令示例：
    ``runserver`` / ``runserver 0.0.0.0:8000`` — 开发 HTTP 服务（WebSocket 需用 Daphne/Uvicorn 等 ASGI）。
    ``migrate`` / ``makemigrations`` — 数据库迁移。
    ``createsuperuser`` — 创建管理员账号。
    ``shell`` — 交互式 Django Shell。

环境变量 ``DJANGO_SETTINGS_MODULE`` 指向 ``breeding_system.settings``。
"""
import os
import sys


def main():
    """
    运行管理任务的主入口函数。
    设置 Django 设置模块的环境变量并执行命令行指令。
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'breeding_system.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "无法导入 Django。请确保它已安装并在您的 PYTHONPATH 环境变量中可用。"
            "您是否忘记激活虚拟环境？"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    # Security dependency refresh keeps the management entry point unchanged.
    main()
