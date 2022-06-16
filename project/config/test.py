from __future__ import absolute_import
from .settings import *

import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("ENABLE_DEBUG", "False") == "True"
# DATABASES = {
#    'default': {
#        'ENGINE': os.environ["DB_ENGINE"],
#        'NAME': os.environ["DB_NAME"],
#        'USER': os.environ["TEST_DB_USER"],
#        'PASSWORD': os.environ["TEST_DB_PASSWORD"],
#		'OPTIONS': {
#			'threaded': True,
#		}
#    }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
