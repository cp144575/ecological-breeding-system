"""
================================================================================
生态养殖系统 — Django 全局配置（``breeding_system.settings``）
================================================================================

本模块集中定义：
    - 路径、密钥、调试开关、允许主机
    - ``INSTALLED_APPS``：含 Django 内置、第三方（DRF/JWT/CORS/Channels）及业务应用
    - 数据库、静态/媒体文件、国际化与时区
    - REST Framework、JWT、分页与过滤器
    - Channels（WebSocket）使用的 Channel Layer（开发默认内存层）

部署提示：
    - 生产环境须关闭 ``DEBUG``，收紧 ``ALLOWED_HOSTS``，更换 ``SECRET_KEY``，
      数据库密码勿入库可使用环境变量；多进程 WebSocket 建议使用 Redis Channel Layer。
    - 对外溯源链接可通过环境变量 ``TRACE_PUBLIC_BASE_URL`` 指定前端公网域名。
================================================================================
"""

from pathlib import Path
import os

# -----------------------------------------------------------------------------
# 路径：项目根目录（与管理脚本、apps、media 等同级）
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# 加载项目根目录下的 .env 文件（密钥、数据库密码等隐私配置放在 .env 中，不入库）
# 未安装 python-dotenv 时静默跳过，此时使用下方 os.environ 的默认值
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass


# -----------------------------------------------------------------------------
# 基础安全与运行模式
# -----------------------------------------------------------------------------
# 密钥从环境变量读取；生产环境务必设置 DJANGO_SECRET_KEY（可用 get_random_secret_key 生成）
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-本地开发默认密钥-请勿用于生产环境')

# 调试模式（生产环境需关闭）：.env 中设置 DJANGO_DEBUG=False
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

# 允许访问的主机，逗号分隔；开发环境默认 *
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',') if h.strip()]

# 溯源二维码中写入的公开页基础 URL；为空时由 ``traceability_app.models._build_public_trace_url`` 按 DEBUG 推导
TRACE_PUBLIC_BASE_URL = os.getenv('TRACE_PUBLIC_BASE_URL', '').strip()


# -----------------------------------------------------------------------------
# 已安装应用（顺序建议：daphne → Django 内置 → 第三方 → 本项目 apps.*）
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 第三方扩展
    'rest_framework',
    'corsheaders',
    'django_filters',
    'channels',
    
    # 业务模块
    'apps.core',
    'apps.users',
    'apps.livestock',
    'apps.production',
    'apps.stats',
    'apps.traceability_app',
]

# -----------------------------------------------------------------------------
# 中间件（自上而下执行请求，自下而上返回响应）
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # 跨域中间件
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'breeding_system.urls'

# -----------------------------------------------------------------------------
# 模板（本项目以后台 API + 前端 SPA 为主，模板多用于 Admin）
# -----------------------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# HTTP 同步入口（Gunicorn+uWSGI 等）；实时推送见下方 ASGI + Channels
WSGI_APPLICATION = 'breeding_system.wsgi.application'
# 异步入口：HTTP + WebSocket（``breeding_system.asgi`` 内 ProtocolTypeRouter）
ASGI_APPLICATION = 'breeding_system.asgi.application'

# -----------------------------------------------------------------------------
# Django Channels：实时广播（如列表刷新）。单机开发可用内存后端；多 Worker 须 Redis
# -----------------------------------------------------------------------------
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}


# -----------------------------------------------------------------------------
# 数据库（MySQL；敏感信息建议改为 os.environ）
# -----------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        # 数据库连接信息从 .env 读取，避免将密码提交到 GitHub
        'NAME': os.environ.get('DB_NAME', 'ecological_breeding_system'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}

# -----------------------------------------------------------------------------
# 认证：扩展用户模型位于 apps.users.models.User
# -----------------------------------------------------------------------------
AUTH_USER_MODEL = 'users.User'

# -----------------------------------------------------------------------------
# Django REST framework：全局认证 / 权限 / 分页 / 过滤与搜索
# -----------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.StandardPagination',
    'DEFAULT_PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
}

# -----------------------------------------------------------------------------
# Simple JWT：访问令牌与刷新令牌生命周期、签名算法等
# -----------------------------------------------------------------------------
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# -----------------------------------------------------------------------------
# 跨域（开发阶段允许全部来源；生产应改为白名单域名）
# -----------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True


# -----------------------------------------------------------------------------
# 密码强度校验（创建用户 / 改密码时生效）
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# -----------------------------------------------------------------------------
# 国际化与时区（USE_TZ=False：naive 本地时间）
# -----------------------------------------------------------------------------
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = False # 关闭 UTC，使用本地时间


# -----------------------------------------------------------------------------
# 静态文件（收集命令 ``collectstatic`` 输出到 STATIC_ROOT）
# -----------------------------------------------------------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'collect_static')

# -----------------------------------------------------------------------------
# 用户上传媒体（头像、证照、批次图片等；开发环境 urls.py 会挂载 MEDIA 路由）
# -----------------------------------------------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# -----------------------------------------------------------------------------
# ORM 默认主键（BigAutoField）
# -----------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
