from __future__ import absolute_import
from .settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("ENABLE_DEBUG", "False") == "True"
DATABASES = {
    'default': {
        'ENGINE': os.environ["DB_ENGINE"],
        'NAME': os.environ["DB_NAME"],
        'USER': os.environ["DB_USER"],
        'PASSWORD': os.environ["DB_PASSWORD"],
        'OPTIONS': {
            'threaded': True,
        }
    }
}
if DEBUG:
    MIDDLEWARE.append('pyha.middleware.NoCache')
    SESSION_COOKIE_SECURE = False

    if not os.environ.get("EMAIL_BACKEND_FILE_PATH") == None:
        EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
        EMAIL_FILE_PATH = os.environ["EMAIL_BACKEND_FILE_PATH"]
    else:
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
