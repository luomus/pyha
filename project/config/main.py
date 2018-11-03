from __future__ import absolute_import
from .settings import *

import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ["ENABLE_DEBUG"] == "True"
DATABASES = {
    'default': {
        'ENGINE': os.environ["DB_ENGINE"],
        'NAME': os.environ["DB_NAME"],
        'USER': os.environ["DB_USER"],
        'PASSWORD': os.environ["DB_PASSWORD"]
    }
}
if(DEBUG): EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend' 
else: EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
