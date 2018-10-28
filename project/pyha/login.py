import json
from django.urls import reverse

import base64
from functools import wraps
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.http import HttpResponseRedirect
from pyha.models import Collection, Request, StatusEnum
from pyha.roles import HANDLER_SENS, USER, HANDLER_ANY, HANDLER_COLL
from pyha.warehouse import is_download_handler, get_collections_where_download_handler
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
            if HANDLER_SENS in r:
                request.session["user_roles"].append(r)
        request.session["token"] = token
        if not "_language" in request.session:
            request.session["_language"] = "fi"
        add_collection_request_handler_roles(request, authentication_info)
        if HANDLER_SENS in request.session["user_roles"] or HANDLER_COLL in request.session["user_roles"]:
            request.session["user_roles"].append(USER)
            request.session["user_roles"].append(HANDLER_ANY)
            request.session["current_user_role"] = HANDLER_ANY
        else:
            request.session["user_roles"] = [USER]
            request.session["current_user_role"] = USER
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
        del request.session["user_name"]
        del request.session["user_email"]
        del request.session["_language"]
        del request.session["user_roles"]
        del request.session["current_user_role"]
        if "has_viewed" in request.session:
            del request.session["has_viewed"]
            return True
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
    #if Collection.objects.filter(downloadRequestHandler__contains=request.session["user_id"]).count() > 0:	
    if is_download_handler(request.session["user_id"]):
        request.session["user_roles"].append(HANDLER_COLL)
        
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
    role1 = HANDLER_SENS in request.session.get("user_roles", [None])
    role2 = HANDLER_COLL in request.session.get("user_roles", [None])
    return allowed_to_view(request, requestId, userId, role1, role2)

def is_request_owner(request, requestId):
    userId = request.session["user_id"]
    return Request.objects.filter(id=requestId, user=userId, status__gte=0).exists()

def allowed_to_view(request, requestId, userId, role1, role2):
    if HANDLER_ANY in request.session.get("current_user_role", [None]):
        if not Request.objects.filter(id=requestId, status__gt=0).exists():
            return False
        currentRequest = Request.objects.get(id=requestId, status__gt=0)
        if role2 and not role1:            
            if(currentRequest.sensstatus == StatusEnum.IGNORE_OFFICIAL):
                if not Collection.objects.filter(request=requestId, address__in = get_collections_where_download_handler(userId), status__gt=0).count() > 0:
                    return False
            else:
                #if not Collection.objects.filter(request=requestId, customSecured__gt = 0, downloadRequestHandler__contains = str(userId), status__gt=0).count() > 0:    
                if not Collection.objects.filter(request=requestId, customSecured__gt = 0, address__in = get_collections_where_download_handler(userId), status__gt=0).count() > 0:
                    return False
    else:
        if not Request.objects.filter(id=requestId, user=userId, status__gte=0).exists():
            return False
    return True
    
def is_allowed_to_ask_information_as_target(request, target, requestId):
    if target == 'sens':
        return HANDLER_SENS in request.session["user_roles"]
    elif Collection.objects.filter(request=requestId, address=target).exists():
        collection = Collection.objects.get(request=requestId, address=target)
        return request.session["user_id"] in collection.downloadRequestHandler
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
