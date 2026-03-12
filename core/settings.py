"""
DJANGO SETTINGS 
Configurado para desarrollo y producción (Railway)
"""

# =========================================================
# IMPORTS
# =========================================================

import os
from pathlib import Path
from decouple import config
import dj_database_url
import stripe


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# SECURITY SETTINGS
# =========================================================

# Clave secreta (se obtiene del .env)
SECRET_KEY = config("SECRET_KEY")

# Debug solo para desarrollo
DEBUG = config("DEBUG", default=False, cast=bool)

# Hosts permitidos
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*").split(",")
CSRF_TRUSTED_ORIGINS = [
    "https://ecommerce-app-production-4a70.up.railway.app"
]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# =========================================================
# INSTALLED APPLICATIONS
# =========================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Apps del proyecto
    'shop',
    'cart',
    'orders',
    'payment',
]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # Sirve archivos estáticos en producción
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# =========================================================
# URLS Y WSGI
# =========================================================

ROOT_URLCONF = 'core.urls'

WSGI_APPLICATION = 'core.wsgi.application'


# =========================================================
# TEMPLATES
# =========================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [BASE_DIR / "templates"],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [

                'django.template.context_processors.debug',
                'django.template.context_processors.request',

                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # carrito de compras
                'cart.context_processors.cart'
            ],
        },
    },
]


# =========================================================
# DATABASE CONFIGURATION
# =========================================================
# Railway usa PostgreSQL automáticamente

DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL", default="sqlite:///db.sqlite3"),
        conn_max_age=600,
        ssl_require=not DEBUG
    )
}


# =========================================================
# PASSWORD VALIDATION
# =========================================================

AUTH_PASSWORD_VALIDATORS = [

    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },

    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },

    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },

    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },

]


# =========================================================
# INTERNATIONALIZATION
# =========================================================

LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# =========================================================
# STATIC FILES
# =========================================================

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# carpeta usada en producción
STATIC_ROOT = BASE_DIR / "staticfiles"

# optimización de archivos estáticos
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True

# =========================================================
# MEDIA FILES
# =========================================================

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# =========================================================
# SESSION SETTINGS
# =========================================================

# carrito de compras
CART_SESSION_ID = "cart"


# =========================================================
# EMAIL CONFIGURATION (GMAIL SMTP)
# =========================================================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# =========================================================
# STRIPE CONFIGURATION
# =========================================================

STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET")

STRIPE_API_VERSION = "2022-11-15"
STRIPE_CURRENCY = "cop"
STRIPE_WEBHOOK_TOLERANCE = 300

stripe.api_key = STRIPE_SECRET_KEY


# =========================================================
# CELERY CONFIGURATION
# =========================================================

CELERY_BROKER_URL = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("REDIS_URL", default="redis://localhost:6379/0")

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'


# =========================================================
# SECURITY / RAILWAY SETTINGS
# =========================================================

# necesario cuando usas proxy (Railway)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# evita errores CSRF en producción
CSRF_TRUSTED_ORIGINS = [
    "https://*.railway.app"
]


# =========================================================
# LOGGING
# =========================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
}


# =========================================================
# DEFAULT PRIMARY KEY
# =========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"