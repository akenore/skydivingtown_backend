from pathlib import Path
from decouple import config
from django.contrib.messages import constants as messages
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'graphene_django',
    'corsheaders',
    'django_countries',
    'allauth',
    'allauth.account',
    'tinymce',
    'secure',
    'event',
    'contract',
    'public',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'django.middleware.locale.LocaleMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

LANGUAGES = (
    ('en', _('English')),
    ('fr', _('French')),
)


STATIC_URL = 'static/'
MEDIA_URL = '/shared/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

CLOUDFLARE_R2_BUCKET = config("CLOUDFLARE_R2_BUCKET")
CLOUDFLARE_R2_BUCKET_ENDPOINT = config("CLOUDFLARE_R2_BUCKET_ENDPOINT")
CLOUDFLARE_R2_ACCESS_KEY = config("CLOUDFLARE_R2_ACCESS_KEY")
CLOUDFLARE_R2_SECRET_KEY = config("CLOUDFLARE_R2_SECRET_KEY")

CLOUDFLARE_R2_CONFIG_OPTIONS = {
    "bucket_name": config("CLOUDFLARE_R2_BUCKET"),
    "default_acl": "public-read",  # or "private"
    "signature_version": "s3v4",
    "endpoint_url": config("CLOUDFLARE_R2_BUCKET_ENDPOINT"),
    "access_key": config("CLOUDFLARE_R2_ACCESS_KEY"),
    "secret_key": config("CLOUDFLARE_R2_SECRET_KEY"),
}

STORAGES = {
    "default": {
        "BACKEND": "helpers.cloudflare.storages.MediaFileStorage",
        "OPTIONS": CLOUDFLARE_R2_CONFIG_OPTIONS,
    },
    "staticfiles": {
        "BACKEND": "helpers.cloudflare.storages.StaticFileStorage",
        "OPTIONS": CLOUDFLARE_R2_CONFIG_OPTIONS,
    },
}


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# EMAIL_HOST = config('EMAIL_HOST', default='localhost')
# EMAIL_PORT = config('EMAIL_PORT', cast=int)
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
# EMAIL_HOST_USER = config('EMAIL_HOST_USER')
# EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)

DEFAULT_FROM_EMAIL = 'SkydivingTown <noreply@skydivingtown.com>'
ADMIN_LIST_EMAILS = ['joudakenore@gmail.com',]

ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGOUT_REDIRECT_URL = "home"
LOGIN_REDIRECT_URL = "myadmin"
ACCOUNT_FORMS = {
    'login': 'config.auth.SignIn',
    # 'signup': 'config.auth.CustomSignupForm',
    'change_password': 'config.auth.ChangePassword',
    'reset_password': 'config.auth.ResetPassword',
    # 'reset_password_from_key': 'config.auth.CustomResetPasswordKeyForm',
}

COUNTRIES_OVERRIDE = {
    'IL': None,
}

MESSAGE_TAGS = {
    messages.DEBUG: 'text-yellow-800 bg-yellow-50 dark:bg-gray-800 dark:text-yellow-300',
    messages.INFO: 'text-blue-800 bg-blue-50 dark:bg-gray-800 dark:text-blue-400',
    messages.SUCCESS: 'text-green-800 bg-green-50 dark:bg-gray-800 dark:text-green-400',
    messages.WARNING: 'text-yellow-800 bg-yellow-50 dark:bg-gray-800 dark:text-yellow-300',
    messages.ERROR: 'text-red-800 bg-red-50 dark:bg-gray-800 dark:text-red-400',

}

TINYMCE_API = config('TINYMCE_API')
TINYMCE_JS_URL = f'https://cdn.tiny.cloud/1/{
    TINYMCE_API}/tinymce/7/tinymce.min.js'

TINYMCE_DEFAULT_CONFIG = {
    "theme": "silver",
    "height": 500,
    "menubar": False,
    "plugins": "advlist,autolink,lists,link,image,charmap,print,preview,anchor,"
    "searchreplace,visualblocks,code,fullscreen,insertdatetime,media,table,paste,"
    "code,help,wordcount",
    "toolbar": "undo redo | formatselect | "
    "bold italic backcolor | alignleft aligncenter "
    "alignright alignjustify | bullist numlist outdent indent | "
    "removeformat | help",
}
TINYMCE_SPELLCHECKER = True
TINYMCE_COMPRESSOR = False
COUNTRIES_OVERRIDE = {
    'IL': None,
}

GRAPHENE = {
    "SCHEMA": "public.schema.schema"
}
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]