"""
Django settings for feedback_api project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Copied from iTheirs settings file.
# TEMPLATE DIRS AND OTHER PROJECT PATHS CONFIGURATION
TEMPLATE_DIR = BASE_DIR.joinpath("templates")
STATIC_DIR = BASE_DIR.joinpath("static")
MEDIA_ROOT = BASE_DIR.joinpath("media")
LOCALE_DIR = BASE_DIR.joinpath("locale")  # 270421


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "192.168.88.31",
    "192.168.88.33",
    "192.168.88.34",
    "192.168.0.100",
    ".vercel.app",
    ".railway.app",
]
PORT = os.getenv("PORT")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "corsheaders",
    "storages",
    "drf_spectacular",
    "rest_framework",
    "django_filters",
    "debug_toolbar",
    "feedback_api.celery.CeleryConfig",
    "user",
    "apps",
    "timeline",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "feedback_api.urls"

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
                "django.template.context_processors.media",
            ],
        },
    },
]

WSGI_APPLICATION = "feedback_api.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DATABASE_NAME"),
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "HOST": os.getenv("DATABASE_HOST"),
        "PORT": os.getenv("DATABASE_PORT"),
        # 'OPTIONS': {
        #     "service": "nine_service",
        #     "passfile": ".nine_pgpass"
        # }
    },
    "test": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = "en-ng"

# TIME_ZONE = 'UTC'
TIME_ZONE = "Africa/Lagos"

# USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

# STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ########################### #
# NINE CUSTOM SETTINGS CONFIG #
#       DECEMBER 7, 2022      #
# ########################### #
AUTH_USER_MODEL = "user.User"
ASGI_APPLICATION = "feedback_api.asgi.application"

# DJANGO REST FRAMEWORK CONFIGURATIONS
"""
The JWTStatelessUserAuthentication backend’s authenticate method does not perform a database lookup to obtain a user 
instance. Instead, it returns a rest_framework_simplejwt.models.TokenUser instance which acts as a stateless user 
object backed only by a validated token instead of a record in a database. This can facilitate developing single 
sign-on functionality between separately hosted Django apps which all share the same token secret key. To use this 
feature, add the rest_framework_simplejwt.authentication.JWTStatelessUserAuthentication backend (instead of the default
JWTAuthentication backend) to the Django REST Framework’s DEFAULT_AUTHENTICATION_CLASSES config setting:
"""
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Use Django standard "django.contrib.auth" permissions, or
    # allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'rest_framework_simplejwt.authentication.JWTStatelessUserAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    # "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.CursorPagination",
    "PAGE_SIZE": 20,
    # "ORDERING":
    # 'DEFAULT_FILTER_BACKENDS': (
    #     'django_filters.rest_framework.DjangoFilterBackend',
    # ),
}

# REST_FRAMEWORK = {
#     #    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
#     'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
#     # 'DEFAULT_PAGINATION_CLASS': 'core.pagination.CustomPagination',
#     'PAGE_SIZE': 10,
#     # 'DATE_INPUT_FORMATS': ["%d/%m/%Y", ],
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         # 'rest_framework_simplejwt.authentication.JWTAuthentication',
#         'rest_framework.authentication.BasicAuthentication',
#         'rest_framework.authentication.SessionAuthentication',
#     ),
#     'TEST_REQUEST_DEFAULT_FORMAT': 'json',
#     # 'EXCEPTION_HANDLER': 'core.utils.custom_exception_handler'
# }

# REST_AUTH_SERIALIZERS = {
#     "USER_DETAILS_SERIALIZER": "napps.serializers.UserSerializer",
# }


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=31),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=90),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    # 'VERIFYING_KEY': None,
    # 'AUDIENCE': None,
    # 'ISSUER': None,
    # 'JWK_URL': None,
    # 'LEEWAY': 0,
    # 'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    # 'USER_ID_FIELD': 'id',
    # 'USER_ID_CLAIM': 'user_id',
    # 'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    #
    # 'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    # 'TOKEN_TYPE_CLAIM': 'token_type',
    # 'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    #
    # 'JTI_CLAIM': 'jti',
    #
    # 'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    # 'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    # 'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
    },
}

SPECTACULAR_SETTINGS = {
    "SCHEMA_PATH_PREFIX": r"/api/v1",
    "DEFAULT_GENERATOR_CLASS": "drf_spectacular.generators.SchemaGenerator",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "COMPONENT_SPLIT_PATCH": True,
    "COMPONENT_SPLIT_REQUEST": True,
    # "SWAGGER_UI_SETTINGS": {
    #     "deepLinking": True,
    #     "persistAuthorization": True,
    #     "displayOperationId": True,
    #     "displayRequestDuration": True
    # },
    "UPLOADED_FILES_USE_URL": True,
    "TITLE": "Nine API",
    "DESCRIPTION": "Nine API Doc",
    "VERSION": "0.1.0",
    "LICENSE": {"name": "BSD License"},
    "CONTACT": {
        "name": os.getenv("API_CONTACT_NAME"),
        "email": os.getenv("API_CONTACT_EMAIL"),
    },
    # Oauth2 related settings. used for example by django-oauth2-toolkit.
    # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.3.md#oauth-flows-object
    "OAUTH2_FLOWS": [],
    "OAUTH2_AUTHORIZATION_URL": None,
    "OAUTH2_TOKEN_URL": None,
    "OAUTH2_REFRESH_URL": None,
    "OAUTH2_SCOPES": None,
}

# CORSHEADER SETTINGS DEFINITIONS
# CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST = [f"http://{_}:3000" for _ in ALLOWED_HOSTS]
CORS_ORIGIN_WHITELIST = [
    "https://nineapp.vercel.app",
    "https://nine-ui.vercel.app",
    "https://*.railway.app",
    "http://localhost:3000",
]
CORS_ALLOW_ALL_ORIGIN = True
CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
    "https://*.netlify.app",
    "https://*.railway.app",
]

# -=-=-=-=-=-=-=-=-=-=-=- #
#   EMAIL CONFIGURATION   #
# -=-=-=-=-=-=-=-=-=-=-=- #
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_HOST_USER = os.getenv("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_DEFAULT_FROM = os.getenv("EMAIL_SENDER")

# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ #
#   User added customization settings.  #
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ #

RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672//"
REDIS_URL = "redis://localhost:6379"
CELERY_BROKER_URL = RABBITMQ_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["application/json", "application/x-python-serialize"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"

CELERY_TIMEZONE = TIME_ZONE

# DJANGO REDIS CONFIGURATION
# CACHES
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "PARSER_CLASS": "redis.connection.HiredisParser",
            "SERIALIZER": "django_redis.serializers.msgpack.MSGPackSerializer",
            # "SERIALIZER_CLASS": "django_redis.serializers.json.JSONSerializer",
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # "CLIENT_CLASS": "django_redis.client.ShardClient",
            # "CLIENT_CLASS": "django_redis.client.HerdClient",
            "IGNORE_EXCEPTIONS": True,
            "SOCKET_CONNECT_TIMEOUT": 5,  # seconds
            "SOCKET_TIMEOUT": 5,  # seconds
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100,
                "retry_on_timeout": True,
                "ssl_cert_reqs": None,
            },
        },
    }
}
DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True

# from django_redis import get_redis_connection
#
# r = get_redis_connection("default")  # Use the name you have defined for Redis in settings.CACHES
# connection_pool = r.connection_pool
# print("Created connections so far: %d" % connection_pool._created_connections)

# SESSION
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# LOGGING
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        # 'file': {
        #     'level': 'ERROR',
        #     'class': 'logging.FileHandler',
        #     'filename': Path.joinpath(BASE_DIR, 'logs/debug.log')
        # },
        "console": {"class": "logging.StreamHandler"}
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    # 'loggers': {
    #     'django': {
    #         'handlers': ['file'],
    #         'level': 'ERROR',
    #         'propagate': True,
    #     },
    # }
}

# ACCOUNT REGISTRATION CODE-GENERATION CONFIGURATION
DIGEST_SIZE = 4

# -=-=-=-=-=-=-=-=  #
#   BOTO3 STORAGE   #
# -=-=-=-=-=-=-=-=  #
# https://ordinarycoders.com/blog/article/serve-django-static-and-media-files-in-production
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN = os.getenv("AWS_S3_CUSTOM_DOMAIN")
AWS_LOCATION = "static"
STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
# ]
DEFAULT_FILE_STORAGE = (
    "feedback_api.storage_backends.MediaStorage"  # The media storage configuration
)

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
#   STATIC FILES AND MEDIA FILES CONFIGURATION    #
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
STATICFILES_DIRS = [STATIC_DIR]
STATIC_ROOT = BASE_DIR.joinpath("staticfiles")
# MEDIAFILES_DIRS = [MEDIA_ROOT]
# MEDIA_URL = "nineapi-production.up.railway.app/media" or "http://192.168.88.34:4000/media/" or "http://192.168.88.33:4000/media/" or "http://192.168.0.100:4000/media/" or "http://localhost:4000/media/"

# LOCALE PATHS - 270421.
LOCALE_PATHS = [LOCALE_DIR]