from datetime import timedelta
from pathlib import Path

from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-90mbkck#1btx7=nbfe=al*m=nz6mj2bl+*360vfa!uzs+ydtjy"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "shop.apps.ShopConfig",
    "cart.apps.CartConfig",
    "orders.apps.OrdersConfig",
    "account.apps.AccountConfig",
    "checkout.apps.CheckoutConfig",
    "zarinpal.apps.ZarinpalConfig",
    "portfolio.apps.PortfolioConfig",
    # Others
    "mathfilters",
    "debug_toolbar",
    "rosetta",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # internationalization
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "myshop.urls"

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
                "cart.context_processors.cart",
                "cart.context_processors.categories",
                "cart.context_processors.wishlist_count",
            ],
        },
    },
]

WSGI_APPLICATION = "myshop.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", _("English")),
    ("fa", _("Persian")),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
# STATIC_ROOT = '../radinstore/static/'
STATIC_ROOT = BASE_DIR / "static"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# #
# پس اگه بخواهم بهتر بگم ما یک دیکشنری داخل دیکشنری داریم
# سیژن ما یک دیکشنری بزرگ است که موارد زیادی میتواند درون آن باشد.
# یکی از آن ها دیکشنری مربوط به سبد خرید است که نام دیکشنری سبد خرید را ما در بخش ستینگ با
# CART_SESSION_ID
# تعیین میکنیم

CART_SESSION_ID = "cart"

# If you don’t want to set up email settings:
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Email server configuration
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "mahdi.emadi90@gmail.com"
EMAIL_HOST_PASSWORD = "wkrjebosvlelmftp"
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# Custom user model
AUTH_USER_MODEL = "account.UserBase"
LOGIN_REDIRECT_URL = "/account/dashboard"
LOGIN_URL = "/account/login/"

# To prevent showing "Debug Toolbar" in production mode
INTERNAL_IPS = [
    "127.0.0.1",
]


# Celery beat
CELERY_BEAT_SCHEDULE = {
    "display-sessions-task": {
        "task": "cart.tasks.display_sessions",
        "schedule": timedelta(minutes=1 / 60),
    },
}

# Using internal memory instead of broker
CELERY_BROKER_URL = "memory://localhost/"
CELERY_RESULT_BACKEND = "rpc://"

# Zarrin Pal
MERCHANT = "00000000-0000-0000-0000-000000000000"
SANDBOX = True
