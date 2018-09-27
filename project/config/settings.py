"""
Django settings for pyha project.

Generated by 'django-admin startproject' using Django 1.10.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os



# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
LOCAL_REQ_URL = 'http://127.0.0.1:8000/pyha/request/'
REQ_URL = os.environ["EMAIL_LINK_URL"] #'https://fmnh-ws-test.it.helsinki.fi/pyha/request/'
LAJIAUTH_URL = os.environ["LAJI_AUTH_URL"] #'https://fmnh-ws-test.it.helsinki.fi/laji-auth/'
LAJIDOW_URL = os.environ["LAJI_ETL_FILE_DOWNLOAD_URL"] #'https://fmnh-ws-test.it.helsinki.fi/laji-etl/download/secured/'
LAJIPERSONAPI_URL = os.environ["TRIPLESTORE_URL"] #'https://fmnh-ws-test.it.helsinki.fi/triplestore/'
LAJIPERSONAPI_USER = os.environ["TRIPLESTORE_USER"]
LAJIPERSONAPI_PW = os.environ["TRIPLESTORE_PASSWORD"]
PDFAPI_URL = os.environ["PDF_API_URL"] #'https://fmnh-ws-prod.it.helsinki.fi/tipu-api/html2pdf'
PDFAPI_USER = os.environ["PDF_API_USER"]
PDFAPI_PW = os.environ["PDF_API_PASSWORD"]
LAJIAPI_URL = os.environ["APILAJIFI_URL"] #'https://apitest.laji.fi/v0/'
LAJIAPI_TOKEN = os.environ["APILAJIFI_TOKEN"]
LAJIFILTERS_URL = LAJIAPI_URL + 'warehouse/filters'
TUN_URL = 'http://tun.fi/'
TARGET= os.environ["LAJI_AUTH_TARGET"] #'KE.541'
HTTPS_USER = os.environ["PYHA_API_USER"] 
HTTPS_PSW = os.environ["PYHA_API_PASSWORD"] 
FILTERS_LINK = os.environ["OBSERVATION_LINK_PREFIX"] #'https://beta.laji.fi/observation/map?'
OFFICIAL_FILTERS_LINK = os.environ["OFFICIAL_OBSERVATION_LINK_PREFIX"] #'https://viranomainen.laji.fi/observation/map?'
SKIP_OFFICIAL = os.environ["SKIP_OFFICIAL"] == "True"
MOCK_JSON=False
APPEND_SLASH=False

DEFAULT_CHARSET = 'utf-8'
FORCE_SCRIPT_NAME = os.environ["DOMAIN_PATH_PREFIX"]
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ["ENABLE_DEBUG"] == "True"


ADMINS = [(os.environ["ADMIN_NAME"], os.environ["ADMIN_EMAIL"])]

SERVER_EMAIL = os.environ["SERVER_EMAIL"]


#should probably also include server external ip and domain.
ALLOWED_HOSTS = ['localhost', '127.0.0.1'
]
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False

# Application definition

INSTALLED_APPS = [
    'pyha.apps.PyhaConfig',
    'django_extensions',
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

CSRF_COOKIE_HTTPONLY = False
ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

# TODO change into oracle database
# also need the JDBC Driver if this runs on JVM
DATABASES = {
    'default': {
        'ENGINE': os.environ["DB_ENGINE"],
        'NAME': os.environ["DB_NAME"],
        'USER': os.environ["DB_USER"],
        'PASSWORD': os.environ["DB_PASSWORD"]
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
    ('sw', _('Ruotsi')),
    ('en', _('Englanti')),
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
STA_URL = os.environ["STATIC_PATH_URL"] + STATIC_URL

STATIC_ROOT = os.path.join(BASE_DIR, "static/")
MEDIA_ROOT	= os.path.join(BASE_DIR, "media/")
