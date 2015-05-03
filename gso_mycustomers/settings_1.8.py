"""
Django settings for mpg project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'm0b2tn#8l^6wrqjkv*!gxq&%)4wvgm1hfgyn$znmg2l#7qgok3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.openid',
    'container',
    'inventory',
    'billing'
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
    )

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'gso_mycustomers.urls'

WSGI_APPLICATION = 'gso_mycustomers.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'gso_mycustomers',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'gso_mycustomers',
        'PASSWORD': 'boudux',
        'HOST': '192.168.1.11',
        'PORT': 5342
    },
}


DATE_FORMAT = 'Y-m-d'

LOGIN_REDIRECT_URL = '/index.html'
LOGOUT_REDIRECT_URL = '/index.html'
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'SCOPE': ['email', 'publish_stream'],
        'METHOD': 'js_sdk'  # instead of 'oauth2'
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 1800
    }
}
# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# TEMPLATES

TEMPLATE_DIRS = (
    'C:/DEV/Sources/gso_mycustomers/resources/templates',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.request",
    "django.core.context_processors.i18n",
    "django.contrib.auth.context_processors.auth",
    "allauth.account.context_processors.account",
    "allauth.socialaccount.context_processors.socialaccount",
) 

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': False,
        'DIRS': ['c:/Documents/Sources/gso_mycustomers/resources/templates/'],
        'OPTIONS': { 'context_processors': (
                         'django.core.context_processors.request',
                         'django.template.context_processors.debug',
                         'django.template.context_processors.i18n',
                         'django.template.context_processors.media',
                         'django.template.context_processors.static',
                         'allauth.account.context_processors.account',
                         'allauth.socialaccount.context_processors.socialaccount',
                         'django.contrib.auth.context_processors.auth',)
                    }
    },
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATICFILES_DIRS = (
    "c:/Documents/Sources/gso_mycustomers/resources/statics/",
)
STATIC_URL = '/statics/'
