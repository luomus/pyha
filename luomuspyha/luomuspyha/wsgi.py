"""
WSGI config for luomuspyha project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
import base64
from functools import wraps
from django.http import HttpResponse, HttpResponseForbidden
from django.core.wsgi import get_wsgi_application
from luomuspyha import secrets

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "luomuspyha.settings")

application = get_wsgi_application()

def basic_auth_required(func):
	@wraps(func)
	def _decorator(request, *args, **kwargs):
		from django.contrib.auth import authenticate, login
		if 'HTTP_AUTHORIZATION' in request.META:
			authmeth, auth = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
			if authmeth.lower() == 'basic':
				auth = base64.b64decode(auth).decode("utf-8")
				if(len(auth.split(':', 1)) == 2):
					username, password = auth.split(':', 1)
					if username == secrets.HTTPS_USER and password == secrets.HTTPS_PSW:
						return func(request, *args, **kwargs)
					else:
						return HttpResponseForbidden('<h1>Forbidden</h1>')
		res = HttpResponse()
		res.status_code = 401
		res['WWW-Authenticate'] = 'Basic'
		return res
	return _decorator