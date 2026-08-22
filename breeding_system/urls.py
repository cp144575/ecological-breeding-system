"""
生态养殖系统 — 根 URLconf（``ROOT_URLCONF``）
============================================

除 ``admin/`` 与各 ``api/*`` 外，根路径 ``''`` 返回 JSON 说明，便于健康检查。
媒体文件在 ``DEBUG`` 下由 ``static()`` 辅助函数挂载（生产一般由 Nginx 指向 ``MEDIA_ROOT``）。
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def api_root_index(request):
    """
    后端 API 根路径说明视图
    
    参数：
        request: HttpRequest 对象
    
    返回值：
        JsonResponse: 包含系统状态和可用 API 模块的 JSON 响应
    """
    return JsonResponse({
        "name": "生态养殖系统后端 API",
        "status": "running",
        "version": "v1.0.0",
        "message": "后端服务已启动，请通过前端开发服务器(默认端口5173)访问系统界面。",
        "endpoints": {
            "users": "/api/users/",
            "livestock": "/api/livestock/",
            "production": "/api/production/",
            "stats": "/api/stats/",
            "traceability": "/api/traceability/",
            "admin": "/admin/"
        }
    })

urlpatterns = [
    # 根路径说明
    path('', api_root_index, name='api_root_index'),
    # 管理后台接口
    path('admin/', admin.site.urls),
    # 用户模块路由
    path('api/users/', include('apps.users.urls')),
    # 牲畜管理模块路由
    path('api/livestock/', include('apps.livestock.urls')),
    # 生产管理模块路由
    path('api/production/', include('apps.production.urls')),
    # 数据统计模块路由
    path('api/stats/', include('apps.stats.urls')),
    # 质量溯源模块路由
    path('api/traceability/', include('apps.traceability_app.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
