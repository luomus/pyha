from __future__ import absolute_import
from .settings import *

import os

#DATABASES = {
#    'default': {
#        'ENGINE': os.environ["DB_ENGINE"],
#        'NAME': os.environ["DB_NAME"],
#        'USER': os.environ["TEST_DB_USER"],
#        'PASSWORD': os.environ["TEST_DB_PASSWORD"]
#    }
#}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
