"""
Django settings for AI Blog Generator project.
"""
import os
import sys
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured
from corsheaders.defaults import default_headers

# Load environment variables
load_dotenv()

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Debug is opt-in: an unconfigured deploy must not leak tracebacks and settings.
DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() == 'true'

# The Django test client speaks plain HTTP. Without this flag, SECURE_SSL_REDIRECT
# below would turn every test request into a 301 before the view is reached, so
# the suite can only run with DEBUG=True - which is not how CI should run it.
TESTING = 'test' in sys.argv[1:2] or os.getenv('DJANGO_TESTING', 'False').lower() == 'true'


def _bool_env(var_name: str, default: bool) -> bool:
    return os.getenv(var_name, str(default)).strip().lower() == 'true'


def _csv_env(var_name: str, default: str = ''):
    value = os.getenv(var_name, default)
    return [item.strip() for item in value.split(',') if item.strip()]


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', '')
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured(
            'DJANGO_SECRET_KEY must be set when DJANGO_DEBUG is not True.'
        )
    SECRET_KEY = 'django-insecure-local-development-only'


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

# Security hardening. The proxy SSL header is only trusted when the deployment
# actually sits behind a TLS-terminating proxy - trusting it otherwise lets a
# client fake HTTPS with a header.
TRUST_PROXY_SSL_HEADER = _bool_env('TRUST_PROXY_SSL_HEADER', not DEBUG)
if TRUST_PROXY_SSL_HEADER:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True

if not DEBUG:
    SECURE_SSL_REDIRECT = _bool_env('SECURE_SSL_REDIRECT', True) and not TESTING
    # Liveness/readiness probes are internal and may arrive over plain HTTP; a
    # 301 there reads as an unhealthy deploy. They expose no data beyond status.
    SECURE_REDIRECT_EXEMPT = [r'^health/live$', r'^health/ready$']
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
    X_FRAME_OPTIONS = 'DENY'

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
    # Fail closed: a view that forgets to declare permissions requires auth
    # instead of being silently public. Public endpoints opt in with AllowAny.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': os.getenv('THROTTLE_ANON', '120/min'),
        'user': os.getenv('THROTTLE_USER', '600/min'),
        # Every generate call spends money at the LLM provider.
        'generate': os.getenv('THROTTLE_GENERATE', '10/min'),
        'engage': os.getenv('THROTTLE_ENGAGE', '30/min'),
        'auth': os.getenv('THROTTLE_AUTH', '10/min'),
    },
    'EXCEPTION_HANDLER': 'ai_blog.apps.core.exceptions.custom_exception_handler',
}

# Password strength. Without this, django.contrib.auth.password_validation
# .validate_password() (used by the registration services) is a silent no-op.
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 10},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# CORS settings
CORS_ALLOWED_ORIGINS = _csv_env(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:5173,http://localhost:3000'
)
CORS_ALLOWED_ORIGIN_REGEXES = _csv_env('CORS_ALLOWED_ORIGIN_REGEXES', '')
CORS_ALLOW_HEADERS = list(default_headers) + [
    'x-request-id',
]

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
ADMIN_INVITE_CODE = os.getenv('ADMIN_INVITE_CODE', '')

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
QUEUE_ALWAYS_SYNC = os.getenv('QUEUE_ALWAYS_SYNC', 'False').lower() == 'true'
QUEUE_SYNC_FALLBACK = os.getenv('QUEUE_SYNC_FALLBACK', str(DEBUG)).lower() == 'true'
CACHE_TTL_SECONDS = int(os.getenv('CACHE_TTL_SECONDS', '60'))

# LocMemCache is per-process, so throttle counters and cached responses are not
# shared between gunicorn workers. Set CACHE_URL (redis://...) in production to
# get a single shared cache; local dev falls back to in-memory.
CACHE_URL = os.getenv('CACHE_URL', '')
if CACHE_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': CACHE_URL,
            'TIMEOUT': CACHE_TTL_SECONDS,
            'KEY_PREFIX': 'ai-blog',
        }
    }
else:
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
