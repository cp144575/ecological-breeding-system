"""
项目根包初始化：在 Django 启动最早阶段把 PyMySQL 注册为 MySQLdb。

说明：
    Django 默认 MySQL 后端期望 ``MySQLdb`` 接口；在 Windows 等环境常用 ``PyMySQL``。
    ``install_as_MySQLdb()`` 让 ``django.db.backends.mysql`` 能正常连接 MySQL，
    需在 ``manage.py`` / ``wsgi`` / ``asgi`` 加载 settings 之前生效（此处随包导入执行）。
"""
import pymysql

pymysql.install_as_MySQLdb()
