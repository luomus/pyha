"""
Django settings for luomuspyha project.

Generated by 'django-admin startproject' using Django 1.10.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from luomuspyha import secrets


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = secrets.SECRET_KEY_1
LOCAL_REQ_URL = 'http://127.0.0.1:8000/pyha/request/'
LAJI_REQ_URL = 'https://fmnh-ws-test.it.helsinki.fi/pyha/request/'
REQ_URL = LOCAL_REQ_URL
LAJIAUTH_URL = 'https://fmnh-ws-test.it.helsinki.fi/laji-auth/'
LAJIDOW_URL = 'https://fmnh-ws-test.it.helsinki.fi/laji-etl/download/secured/'
LAJIPERSONAPI_URL = 'https://fmnh-ws-test.it.helsinki.fi/triplestore/'
LAJIPERSONAPI_USER = 'pyha'
LAJIPERSONAPI_PW = os.environ["PW_1"]
LAJIAPI_URL = 'https://apitest.laji.fi/v0/'
LAJIFILTERS_URL= 'https://apitest.laji.fi/v0/warehouse/filters'
TARGET='KE.541'
HTTPS_USER = 'kivaa'
HTTPS_PSW = 'kivaa'
MOCK_JSON=True
APPEND_SLASH=False

DEFAULT_CHARSET = 'utf-8'
#FORCE_SCRIPT_NAME = '/pyha'
#SECRET_KEY = os.environ['LUOMUS_SECRET_KEY']
#LAJIAUTH_URL = os.environ['LUOMUS_LAJIAUTH_URL']
#TARGET = os.environ['LUOMUS_TARGET']
SESSION_SAVE_EVERY_REQUEST = True

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#should probably also include server external ip and domain.
ALLOWED_HOSTS = ['localhost', '127.0.0.1'
]
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False

# Application definition

INSTALLED_APPS = [
    'pyha.apps.PyhaConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'pyha.middleware.ForceDefaultLanguageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'luomuspyha.urls'

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
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'luomuspyha.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

# TODO change into oracle database
# also need the JDBC Driver if this runs on JVM
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'my_cache_table',
        'TIMEOUT': 86400
    }
}



# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/
from django.utils.translation import ugettext_lazy as _


LANGUAGE_CODE = 'fi'
TIME_ZONE = 'Europe/Helsinki'

LANGUAGES = [
    ('fi', _('Suomi')),
    ('en', _('Englanti')),
    ('sw', _('Ruotsi')),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'pyha', 'locale'),
]

LANGUAGE_SESSION_KEY = "lang"

#USE_I18N = True

#USE_L10N = True

#USE_TZ = True

STATICFILES_FINDERS = (
'django.contrib.staticfiles.finders.FileSystemFinder',
'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STA_URL = STATIC_URL
#STA_URL = '/pyha' + STATIC_URL

STATIC_ROOT = os.path.join(BASE_DIR, "static/")
MEDIA_ROOT	= os.path.join(BASE_DIR, "media/")
