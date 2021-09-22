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
PYHA_URL = os.environ["PYHA_URL"] #'https://fmnh-ws-test.it.helsinki.fi/pyha/'
LAJIAUTH_URL = os.environ["LAJI_AUTH_URL"] #'https://fmnh-ws-test.it.helsinki.fi/laji-auth/'
LAJIDOW_URL = os.environ["LAJI_ETL_FILE_DOWNLOAD_URL"] #'https://fmnh-ws-test.it.helsinki.fi/laji-etl/download/secured/'
LAJIPERSONAPI_URL = os.environ["TRIPLESTORE_URL"] #'https://fmnh-ws-test.it.helsinki.fi/triplestore/'
LAJIPERSONAPI_USER = os.environ["TRIPLESTORE_USER"]
LAJIPERSONAPI_PW = os.environ["TRIPLESTORE_PASSWORD"]
LAJIAPI_URL = os.environ["APILAJIFI_URL"] #'https://apitest.laji.fi/v0/'
LAJIAPI_TOKEN = os.environ["APILAJIFI_TOKEN"]
LAJIFILTERS_URL = LAJIAPI_URL + 'warehouse/filters'
TUN_URL = 'https://tun.fi/'
SECRET_TIMEOUT_PERIOD = 10
TARGET= os.environ["LAJI_AUTH_TARGET"] #'KE.541'
SECRET_STATUS_SUB_DIR = os.environ["ZABBIX_STATUS_SUB_DIR"] #path/to
SECRET_ADMIN_SUB_DIR = os.environ["ADMIN_SUB_DIR"] #path/to
SECRET_HTTPS_USER = os.environ["PYHA_API_USER"]
SECRET_HTTPS_PW = os.environ["PYHA_API_PASSWORD"]
FILTERS_LINK = os.environ["OBSERVATION_LINK_PREFIX"] #'https://beta.laji.fi/observation/map?'
OFFICIAL_FILTERS_LINK = os.environ["OFFICIAL_OBSERVATION_LINK_PREFIX"] #'https://viranomaiset.laji.fi/observation/map?'
AFTER_LOGOUT_URL = os.environ["AFTER_LOGOUT_URL"]
SEND_AUTOMATIC_HANDLER_MAILS = os.environ.get("SEND_AUTOMATIC_HANDLER_MAILS", "False") == "True"
ICT_EMAIL = "helpdesk@laji.fi"
PYHA_EMAIL = "noreply.pyha-staging@laji.fi"
DOWNLOAD_PERIOD_DAYS = 365
MAX_UPLOAD_FILE_SIZE = 10485760
MOCK_JSON=False
TESTING=False
APPEND_SLASH=False

DEFAULT_CHARSET = 'utf-8'
FORCE_SCRIPT_NAME = os.environ.get("DOMAIN_PATH_PREFIX", "")
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

ERROR_RATE_LIMIT = int(os.environ.get("EMAIL_ERROR_RATE_LIMIT", 1800))
ERROR_RATE_KEY_LIMIT = int(os.environ.get("EMAIL_ERROR_RATE_KEY_LIMIT", 100))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'ratelimit': {
            '()': 'pyha.utilities.EmailRateLimitFilter'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        #'logfile': {
        #    'class': 'logging.handlers.RotatingFileHandler',
        #    'filename': 'pyha.log',
        #    'maxBytes': 1024 * 100,
        #    'backupCount': 3,
        #    'filters': ['require_debug_false']
        #},
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false', 'ratelimit']
        }
    },
    'loggers': {
        'django': {
            #'handlers': ['logfile', 'mail_admins'],
            'handlers': ['mail_admins'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),

        },
    },
}

ADMINS = [(os.environ["ADMIN_NAME"], os.environ["ADMIN_EMAIL"])]

SERVER_EMAIL = os.environ["SERVER_EMAIL"]


#should probably also include server external ip and domain.
ALLOWED_HOSTS = ['localhost', '127.0.0.1'
]

CSRF_TRUSTED_ORIGINS = [os.environ["PYHA_HOSTNAME"]]
CSRF_FAILURE_VIEW = 'pyha.views.index.csrf_failure'

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
    'simple_history',
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
    'simple_history.middleware.HistoryRequestMiddleware',
]

CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = True
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
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 86400,
        'OPTIONS': {
            'MAX_ENTRIES': 3000
        }
    },
    'collections': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'pyha_collections_cache_table',
        'TIMEOUT': 86400
    },
    'error_mail': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'pyha_error_mail_cache_table',
        'OPTIONS': {
            'MAX_ENTRIES': os.environ["EMAIL_ERROR_RATE_KEY_LIMIT"]
        },
        'TIMEOUT': os.environ["EMAIL_ERROR_RATE_LIMIT"]
    }
}



# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/
from django.utils.translation import ugettext_lazy as _


LANGUAGE_CODE = 'fi'
TIME_ZONE = 'Europe/Helsinki'

LANGUAGES = [
    ('fi', _('Suomi')),
    ('sv', _('Ruotsi')),
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

STATIC_URL = os.environ.get("STATIC_URL", "/static/")
STA_URL = os.environ.get("STATIC_PATH_URL", "") + STATIC_URL

STATIC_ROOT = os.path.join(BASE_DIR, "static/")
MEDIA_ROOT	= os.path.join(BASE_DIR, "media/")
