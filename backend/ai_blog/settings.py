"""
Django settings for AI Blog Generator project.
"""
import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

# Load environment variables
load_dotenv()

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'

def _csv_env(var_name: str, default: str = ''):
    value = os.getenv(var_name, default)
    return [item.strip() for item in value.split(',') if item.strip()]


ALLOWED_HOSTS = _csv_env('ALLOWED_HOSTS', 'localhost,127.0.0.1')
CSRF_TRUSTED_ORIGINS = _csv_env('CSRF_TRUSTED_ORIGINS', '')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    # Third party
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    # Local apps
    'ai_blog.apps.blog',
    'ai_blog.apps.core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'ai_blog.apps.core.middleware.RequestIDMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ai_blog.urls'

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

WSGI_APPLICATION = 'ai_blog.wsgi.application'

# Database
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'ai_blog'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Custom primary key type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'EXCEPTION_HANDLER': 'ai_blog.apps.core.exceptions.custom_exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}

# CORS settings
CORS_ALLOWED_ORIGINS = _csv_env(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:5173,http://localhost:3000'
)
CORS_ALLOWED_ORIGIN_REGEXES = _csv_env('CORS_ALLOWED_ORIGIN_REGEXES', '')

CORS_ALLOW_CREDENTIALS = True

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Anthropic API
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

# Claude Model Configuration
CLAUDE_DEFAULT_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
CLAUDE_FAST_MODEL = os.getenv('CLAUDE_FAST_MODEL', CLAUDE_DEFAULT_MODEL)
CLAUDE_MAX_RETRIES = int(os.getenv('CLAUDE_MAX_RETRIES', '1'))
CLAUDE_TIMEOUT = int(os.getenv('CLAUDE_TIMEOUT', '60'))
CLAUDE_FAST_TIMEOUT = int(os.getenv('CLAUDE_FAST_TIMEOUT', '30'))
FAST_MAX_TOKENS = int(os.getenv('FAST_MAX_TOKENS', '650'))
FAST_MIN_WORDS = int(os.getenv('FAST_MIN_WORDS', '180'))
FAST_MAX_WORDS = int(os.getenv('FAST_MAX_WORDS', '260'))
NORMAL_MIN_WORDS = int(os.getenv('NORMAL_MIN_WORDS', '800'))
NORMAL_MAX_WORDS = int(os.getenv('NORMAL_MAX_WORDS', '1200'))
LLM_CIRCUIT_FAILURE_THRESHOLD = int(os.getenv('LLM_CIRCUIT_FAILURE_THRESHOLD', '3'))
LLM_CIRCUIT_COOL_OFF_SECONDS = int(os.getenv('LLM_CIRCUIT_COOL_OFF_SECONDS', '30'))

# LLM provider configuration
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'anthropic').strip().lower()
ADMIN_AUTH_REQUIRED = os.getenv('ADMIN_AUTH_REQUIRED', 'False').lower() == 'true'

# Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
GEMINI_FAST_MODEL = os.getenv('GEMINI_FAST_MODEL', GEMINI_MODEL)

# Queue / caching configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = int(os.getenv('CELERY_TASK_TIME_LIMIT', '300'))
QUEUE_SYNC_FALLBACK = os.getenv('QUEUE_SYNC_FALLBACK', str(DEBUG)).lower() == 'true'
CACHE_TTL_SECONDS = int(os.getenv('CACHE_TTL_SECONDS', '60'))

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'ai-blog-cache',
        'TIMEOUT': CACHE_TTL_SECONDS,
    }
}


def _validate_llm_config():
    def _is_missing_or_placeholder(value: str) -> bool:
        if not value:
            return True
        lower = value.strip().lower()
        return (
            lower.startswith('replace_with_')
            or lower.startswith('your-')
            or 'api-key-here' in lower
        )

    if LLM_PROVIDER not in {'anthropic', 'gemini'}:
        raise ImproperlyConfigured("LLM_PROVIDER must be either 'anthropic' or 'gemini'")

    if LLM_PROVIDER == 'anthropic':
        if _is_missing_or_placeholder(ANTHROPIC_API_KEY):
            raise ImproperlyConfigured("ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic")
        if not CLAUDE_DEFAULT_MODEL:
            raise ImproperlyConfigured("CLAUDE_MODEL is required when LLM_PROVIDER=anthropic")

    if LLM_PROVIDER == 'gemini':
        if _is_missing_or_placeholder(GEMINI_API_KEY):
            raise ImproperlyConfigured("GEMINI_API_KEY is required when LLM_PROVIDER=gemini")
        if not GEMINI_MODEL:
            raise ImproperlyConfigured("GEMINI_MODEL is required when LLM_PROVIDER=gemini")


_validate_llm_config()

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'ai_blog': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
