
import os
from datetime import timedelta
from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")


# --------------------------------------------------
# Core
# --------------------------------------------------

DEBUG = env.bool("DJANGO_DEBUG", default=True)

SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured(
            "Set DJANGO_SECRET_KEY when DJANGO_DEBUG is False."
        )
    SECRET_KEY = get_random_secret_key()

ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1"],
)

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"

USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --------------------------------------------------
# Security / CORS / CSRF
# --------------------------------------------------

CORS_ALLOWED_ORIGINS = env.list(
    "DJANGO_CORS_ALLOWED_ORIGINS",
    default=[],
)
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = env.list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    default=[],
)


# --------------------------------------------------
# Applications
# --------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "corsheaders",
    "django_filters",

    # Local apps
    "apps.common.apps.CommonConfig",
    "apps.accounts.apps.AccountsConfig",
    "apps.consultants",
    "apps.visas.apps.VisasConfig",
    "apps.appointments",
    "apps.dashboard",
]


# --------------------------------------------------
# Middleware
# --------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# --------------------------------------------------
# URL / WSGI / ASGI
# --------------------------------------------------

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# --------------------------------------------------
# Templates
# --------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# --------------------------------------------------
# Database
# --------------------------------------------------

POSTGRES_DB = env.str("POSTGRES_DB", default="")
USE_SQLITE = env.bool("DJANGO_USE_SQLITE", default=DEBUG and not POSTGRES_DB)

if USE_SQLITE:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
            "OPTIONS": {"timeout": 20},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": POSTGRES_DB or "voyavisa",
            "USER": env.str("POSTGRES_USER", default="postgres"),
            "PASSWORD": env.str("POSTGRES_PASSWORD", default=""),
            "HOST": env.str("POSTGRES_HOST", default="localhost"),
            "PORT": env.str("POSTGRES_PORT", default="5432"),
            "CONN_MAX_AGE": 60,
            "CONN_HEALTH_CHECKS": True,
        }
    }


# --------------------------------------------------
# Custom User
# --------------------------------------------------

AUTH_USER_MODEL = "accounts.User"

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


# --------------------------------------------------
# Django REST Framework
# --------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",

    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],

    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.accounts.authentication.CookieJWTAuthentication",
    ],

    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],

    "DEFAULT_THROTTLE_RATES": {
        "otp": "2/min",
    },
}


# --------------------------------------------------
# Swagger / OpenAPI
# --------------------------------------------------

SPECTACULAR_SETTINGS = {
    "TITLE": "VoyaVisa API",
    "DESCRIPTION": "VoyaVisa Visa and Travel Services API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}


# --------------------------------------------------
# JWT
# --------------------------------------------------

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,

    "UPDATE_LAST_LOGIN": True,
}

JWT_ACCESS_COOKIE = "voyavisa_access"
JWT_REFRESH_COOKIE = "voyavisa_refresh"

JWT_COOKIE_HTTP_ONLY = True
JWT_COOKIE_SECURE = not DEBUG

JWT_COOKIE_SAMESITE = env.str(
    "DJANGO_COOKIE_SAMESITE",
    default="Lax",
)

if JWT_COOKIE_SAMESITE not in {"Lax", "Strict", "None"}:
    raise ImproperlyConfigured(
        "DJANGO_COOKIE_SAMESITE must be Lax, Strict, or None."
    )

if JWT_COOKIE_SAMESITE == "None" and DEBUG:
    raise ImproperlyConfigured(
        "Cross-site cookies require HTTPS with DJANGO_DEBUG=False."
    )

JWT_COOKIE_PATH = "/"


# --------------------------------------------------
# CSRF Cookie
# --------------------------------------------------

CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = JWT_COOKIE_SAMESITE


# --------------------------------------------------
# Static / Media
# --------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# --------------------------------------------------
# Appointment Payments
# --------------------------------------------------

APPOINTMENT_PAYMENT_CARD = env.str(
    "APPOINTMENT_PAYMENT_CARD",
    default="",
).strip()

APPOINTMENT_RECEIPT_ROOT = (
    BASE_DIR / "private_media" / "appointment_receipts"
)


# --------------------------------------------------
# SMS.ir
# --------------------------------------------------

SMSIR_API_KEY = env.str("SMSIR_API_KEY", default="").strip()

SMSIR_OTP_TEMPLATE_ID = env.str(
    "SMSIR_OTP_TEMPLATE_ID",
    default="",
).strip()


# --------------------------------------------------
# Logging
# --------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
