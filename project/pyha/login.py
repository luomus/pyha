import json
from django.urls import reverse

import base64
from functools import wraps
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core import serializers
from pyha.log_utils import changed_by_session_user
from pyha.models import Collection, Request, StatusEnum, AdminUserSettings
from pyha.roles import CAT_ADMIN, ADMIN, USER, HANDLER_ANY, CAT_HANDLER_COLL
from pyha.warehouse import is_download_handler, get_collections_where_download_handler, is_download_handler_in_collection
from pyha import toast
import requests


def _get_authentication_info(token):
    '''
    Get authentication info for the token.
    :param token: The token returned by LajiAuth.
    :return: Authentication info content.
    '''
    url = settings.LAJIAUTH_URL + "token/" + token
    response = requests.get(url, timeout=settings.SECRET_TIMEOUT_PERIOD)
    if response.status_code != 200:
        return None
    else:
        content = json.loads(response.content.decode('utf-8'))
        return content

def log_in(http_request, token, authentication_info):
    '''
    Create session for the request.
    :param http_request: A HttpRequest to create session for.
    :param token: The token returned by LajiAuth.
    :param authentication_info: Authentication information from LajiAuth.
    :return: true if user was succesfully logged in
    '''
    if not "user_id" in http_request.session:
        http_request.session["user_id"] = authentication_info["user"]["qname"]
        http_request.session["user_name"] = authentication_info["user"]["name"]
        http_request.session["user_email"] = authentication_info["user"]["email"]
        http_request.session["user_roles"] = []
        for r in authentication_info["user"]["roles"]:
            if any(role in r for role in [CAT_ADMIN]):
                http_request.session["user_roles"].append(r)
        http_request.session["token"] = token
        if not "_language" in http_request.session:
            http_request.session["_language"] = "fi"
        add_collection_request_handler_roles(http_request, authentication_info)
        http_request.session["user_roles"].append(USER)
        http_request.session["current_user_role"] = USER
        if CAT_HANDLER_COLL in http_request.session["user_roles"]:
            http_request.session["user_roles"].append(HANDLER_ANY)
            http_request.session["current_user_role"] = HANDLER_ANY
        if CAT_ADMIN in http_request.session["user_roles"]:
            http_request.session["user_roles"].append(ADMIN)
            http_request.session["current_user_role"] = ADMIN
            admin, created = User.objects.get_or_create(
                username = http_request.session["user_id"],
                defaults={
                    'first_name': http_request.session["user_name"].split()[0],
                    'last_name': http_request.session["user_name"].split()[-1],
                    'email': http_request.session["user_email"],
                    'password': token,
                    'is_staff': True,
                    'is_active': True,
                    'is_superuser': True
                })
            if not AdminUserSettings.objects.filter(user=http_request.session["user_id"]).exists():
                user_settings = AdminUserSettings()
                user_settings.user = http_request.session["user_id"]
                user_settings.changedBy = changed_by_session_user(http_request)
                user_settings.save()
            login(http_request, admin)
        http_request.session.set_expiry(3600)
        return True
    return False

def log_out(http_request):
    '''
	Clear session for the request.
	:param http_request:
	:return: true if user was succesfully logged out
	'''
    if "user_id" in http_request.session:
        del http_request.session["user_id"]
        http_request.session.flush()
        return False

def authenticate(http_request, token, result):
    '''
    Logs user in if the token is valid.
    :param http_request: A HttpRequest to create session for
    :param token: The token returned by LajiAuth.
    :return: true if user is authenticated succesfully
    '''
    if result is None:
        return False
    else:
        log_in(http_request, token, result)
        return True

def get_user_name(http_request):
    if "user_name" in http_request.session:
        return http_request.session["user_name"]

def add_collection_request_handler_roles(http_request, content):
    if is_download_handler(http_request.session["user_id"]):
        http_request.session["user_roles"].append(CAT_HANDLER_COLL)

def logged_in(http_request):
    if "user_id" in http_request.session:
        return True
    return False

def _process_auth_response(http_request, indexpath):
    if not "token" in http_request.POST:
        return HttpResponseRedirect(settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next='+str(indexpath))
    token = http_request.POST["token"]
    result = _get_authentication_info(token)
    if authenticate(http_request, token, result):
        return HttpResponseRedirect(reverse('pyha:root')+result["next"])
    else:
        return HttpResponseRedirect(settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next='+str(indexpath))

def is_allowed_to_view(http_request, requestId):
    userId = http_request.session["user_id"]
    role2 = CAT_HANDLER_COLL in http_request.session.get("user_roles", [None])
    return allowed_to_view(http_request, requestId, userId, role2)

def is_allowed_to_handle(http_request, requestId):
    userId = http_request.session["user_id"]
    role2 = CAT_HANDLER_COLL in http_request.session.get("user_roles", [None])
    return allowed_to_handle(http_request, requestId, userId, role2)

def is_admin_frozen_and_not_admin(http_request, userRequest):
    if(userRequest.frozen and not ADMIN in http_request.session["current_user_role"]):
        http_request.session["toast"] = {"status": toast.ERROR , "message": ugettext('error_request_has_been_frozen_by_admin')}
        http_request.session.save()
        return True
    else:
        return False

def is_admin_frozen(http_request, userRequest):
    if(userRequest.frozen):
        http_request.session["toast"] = {"status": toast.ERROR , "message": ugettext('error_request_has_been_frozen_by_admin')}
        http_request.session.save()
        return True
    else:
        return False

def is_request_owner(http_request, requestId):
    userId = http_request.session["user_id"]
    return Request.objects.filter(id=requestId, user=userId, status__gte=0).exists()

def is_admin(http_request):
    return ADMIN in http_request.session.get("current_user_role", [None])

def allowed_to_view(http_request, requestId, userId, role2):
    if ADMIN in http_request.session.get("current_user_role", [None]):
        if not Request.objects.filter(id=requestId, status__gt=0).exists():
            return False
    elif HANDLER_ANY in http_request.session.get("current_user_role", [None]):
        if not Request.objects.filter(id=requestId, status__gt=0).exists():
            return False
        currentRequest = Request.objects.get(id=requestId, status__gt=0)
        if role2:
            if not Collection.objects.filter(request=requestId, address__in = get_collections_where_download_handler(userId), status__gt=0).count() > 0:
                return False
    else:
        if not Request.objects.filter(id=requestId, user=userId, status__gte=0).exists():
            return False
    return True

def allowed_to_handle(http_request, requestId, userId, role2):
    if ADMIN in http_request.session.get("current_user_role", [None]):
        if not Request.objects.filter(id=requestId, status__gt=0).exists():
            return False
    elif HANDLER_ANY in http_request.session.get("current_user_role", [None]):
        if not Request.objects.filter(id=requestId, status__gt=0).exists():
            return False
        currentRequest = Request.objects.get(id=requestId, status__gt=0)
        if role2:
            if not Collection.objects.filter(request=requestId, address__in = get_collections_where_download_handler(userId), status__gt=0).count() > 0:
                return False
    else:
        return False
    return True

def is_allowed_to_ask_information_as_target(http_request, target, requestId):
    if target == 'admin':
        return CAT_ADMIN in http_request.session["user_roles"]
    elif Collection.objects.filter(request=requestId, address=target).exists():
        return is_download_handler_in_collection(http_request.session["user_id"], target)
    return False

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
                    if username == settings.SECRET_HTTPS_USER and password == settings.SECRET_HTTPS_PW:
                        return func(request, *args, **kwargs)
                    else:
                        return HttpResponseForbidden('<h1>Forbidden</h1>')
        res = HttpResponse()
        res.status_code = 401
        res['WWW-Authenticate'] = 'Basic realm="Pyha"'
        return res
    return _decorator
