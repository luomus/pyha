from __future__ import absolute_import
from .settings import *

import os

DATABASES = {
    'default': {
        'ENGINE': os.environ["DB_ENGINE"],
        'NAME': os.environ["DB_NAME"],
        'USER': os.environ["DB_USER"],
        'PASSWORD': os.environ["DB_PASSWORD"]
    }
}
