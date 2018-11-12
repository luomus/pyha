import json
from django.urls import reverse

import base64
from functools import wraps
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext
from pyha.models import Collection, Request, StatusEnum, Sens_StatusEnum
from pyha.roles import CAT_ADMIN, ADMIN, CAT_HANDLER_SENS, USER, HANDLER_ANY, CAT_HANDLER_COLL
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

def log_in(request, token, authentication_info):
    '''
    Create session for the request.
    :param request: A HttpRequest to create session for.
    :param token: The token returned by LajiAuth.
    :param authentication_info: Authentication information from LajiAuth.
    :return: true if user was succesfully logged in                      
    '''
    if not "user_id" in request.session:
        request.session["user_id"] = authentication_info["user"]["qname"]
        request.session["user_name"] = authentication_info["user"]["name"]
        request.session["user_email"] = authentication_info["user"]["email"]
        request.session["user_roles"] = []
        for r in authentication_info["user"]["roles"]:
            if any(role in r for role in (CAT_HANDLER_SENS, CAT_ADMIN)):
                request.session["user_roles"].append(r)
        request.session["token"] = token
        if not "_language" in request.session:
            request.session["_language"] = "fi"
        add_collection_request_handler_roles(request, authentication_info)
        request.session["user_roles"].append(USER)
        request.session["current_user_role"] = USER
        if CAT_HANDLER_SENS in request.session["user_roles"] or CAT_HANDLER_COLL in request.session["user_roles"]:
            request.session["user_roles"].append(HANDLER_ANY)
            request.session["current_user_role"] = HANDLER_ANY
        if CAT_ADMIN in request.session["user_roles"]:
            request.session["user_roles"].append(ADMIN)
            request.session["current_user_role"] = ADMIN
        request.session.set_expiry(3600)
        return True
    return False

def log_out(request):
    '''
	Clear session for the request.
	:param request:
	:return: true if user was succesfully logged out                      
	'''
    if "user_id" in request.session:     
        del request.session["user_id"]      
        request.session.flush()
        return False

def authenticate(request, token, result):
    '''
    Logs user in if the token is valid.
    :param request: A HttpRequest to create session for
    :param token: The token returned by LajiAuth.
    :return: true if user is authenticated succesfully
    '''
    if result is None:
        return False
    else:
        log_in(request, token, result)
        return True

def get_user_name(request):
    if "user_name" in request.session:
        return request.session["user_name"]

def add_collection_request_handler_roles(request, content):
    if is_download_handler(request.session["user_id"]):
        request.session["user_roles"].append(CAT_HANDLER_COLL)
        
def logged_in(request):
    if "user_id" in request.session:
        return True
    return False

def _process_auth_response(request, indexpath):
    if not "token" in request.POST:
        return HttpResponseRedirect(settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next='+str(indexpath))
    token = request.POST["token"]
    result = _get_authentication_info(token)
    if authenticate(request, token, result):
        return HttpResponseRedirect(reverse('pyha:root')+result["next"])
    else:
        return HttpResponseRedirect(settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next='+str(indexpath))
        
def is_allowed_to_view(request, requestId):
    userId = request.session["user_id"]
    role1 = CAT_HANDLER_SENS in request.session.get("user_roles", [None])
    role2 = CAT_HANDLER_COLL in request.session.get("user_roles", [None])
    return allowed_to_view(request, requestId, userId, role1, role2)

def is_admin_frozen_and_not_admin(request, userRequest):
    if(userRequest.frozen and not ADMIN in request.session["current_user_role"]):
        request.session["toast"] = {"status": toast.ERROR , "message": ugettext('error_request_has_been_frozen_by_admin')}
        request.session.save()
        return True
    else:
        return False

def is_request_owner(request, requestId):
    userId = request.session["user_id"]
    return Request.objects.filter(id=requestId, user=userId, status__gte=0).exists()

def is_admin(request):
    return ADMIN in request.session.get("current_user_role", [None])

def allowed_to_view(request, requestId, userId, role1, role2):
    if ADMIN in request.session.get("current_user_role", [None]):
        if not Request.objects.filter(id=requestId, status__gt=0).exists():
            return False
    elif HANDLER_ANY in request.session.get("current_user_role", [None]):
        if not Request.objects.filter(id=requestId, status__gt=0).exists():
            return False
        currentRequest = Request.objects.get(id=requestId, status__gt=0)
        if role2 and not role1:            
            if(currentRequest.sensstatus == Sens_StatusEnum.IGNORE_OFFICIAL):
                if not Collection.objects.filter(request=requestId, address__in = get_collections_where_download_handler(userId), status__gt=0).count() > 0:
                    return False
            else:
                if not Collection.objects.filter(request=requestId, customSecured__gt = 0, address__in = get_collections_where_download_handler(userId), status__gt=0).count() > 0:
                    return False
    else:
        if not Request.objects.filter(id=requestId, user=userId, status__gte=0).exists():
            return False
    return True
    
def is_allowed_to_ask_information_as_target(request, target, requestId):
    if target == 'admin':
        return CAT_ADMIN in request.session["user_roles"]
    elif target == 'sens':
        return CAT_HANDLER_SENS in request.session["user_roles"]
    elif Collection.objects.filter(request=requestId, address=target).exists():
        return is_download_handler_in_collection(request.session["user_id"], target)
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
