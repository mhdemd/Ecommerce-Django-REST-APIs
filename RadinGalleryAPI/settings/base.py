import os
from datetime import timedelta
from pathlib import Path

from decouple import config

# ---------------------------------------------------------
# Base settings
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = True
ALLOWED_HOSTS = []

SITE_URL = "http://127.0.0.1:8000"


# ---------------------------------------------------------
# Installed Apps
# ---------------------------------------------------------
INSTALLED_APPS = [
    # Default Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "rest_framework_simplejwt.token_blacklist",
    # Internal apps
    "authentication",
    "products",
    "brands",
    "categories",
    "wishlist",
    "reviews",
    "cart",
    "order",
]


# ---------------------------------------------------------
# Middleware
# ---------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ---------------------------------------------------------
# URL & WSGI Configurations
# ---------------------------------------------------------
ROOT_URLCONF = "RadinGalleryAPI.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "RadinGalleryAPI.wsgi.application"


# ---------------------------------------------------------
# Database
# ---------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": "postgres_db",
        "PORT": "5432",
    }
}


# ---------------------------------------------------------
# Redis
# ---------------------------------------------------------
REDIS_HOST = "redis_cache"
REDIS_PORT = 6379
REDIS_DB = 0

import redis

REDIS_INSTANCE = redis.StrictRedis(
    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
)


# ---------------------------------------------------------
# Cache
# ---------------------------------------------------------
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis_cache:6379",
        "OPTIONS": {
            "DB": 0,
        },
    }
}


# ---------------------------------------------------------
# Authentication & User Model
# ---------------------------------------------------------
AUTH_USER_MODEL = "authentication.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 9,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ---------------------------------------------------------
# Internationalization & Timezone
# ---------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------
# Static & Media Files
# ---------------------------------------------------------
STATIC_URL = "static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = Path(BASE_DIR).parent / "media"


# ---------------------------------------------------------
# Django REST Framework & JWT Settings
# ---------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    # Swagger UI
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Throttling
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "20/min",
        "anon": "10/min",
    },
    # Filtering
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
    ],
    # Pagination
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),  # timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}


# ---------------------------------------------------------
# DRF Spectacular (Swagger) Settings
# ---------------------------------------------------------
from .spectacular import SPECTACULAR_SETTINGS

# ---------------------------------------------------------
# Email Settings
# ---------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@example.com"
EMAIL_VERIFICATION_TOKEN_EXPIRY = 1


# ---------------------------------------------------------
# Default primary key field type
# ---------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------
# CELERY
# ---------------------------------------------------------
# Redis as broker
CELERY_BROKER_URL = "redis://redis_cache:6379/0"

# Store task results in Django database
CELERY_RESULT_BACKEND = "django-db"

# Optional: Enable Celery task result tracking
INSTALLED_APPS += [
    "django_celery_results",
]


# ---------------------------------------------------------
# LOGGING
# ---------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "debug.log"),
            "formatter": "verbose",
        },
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "authentication": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "console": {
            "handlers": ["null"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
