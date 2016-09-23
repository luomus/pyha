import requests
from django.shortcuts import redirect
from django.conf import settings
from django.db import models
from collections import namedtuple
import json

def store(jsond):
        x = json.loads(jsond, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
        print x.email
        print x


