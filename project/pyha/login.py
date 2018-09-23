import json

from django.conf import settings
from django.http import HttpResponseRedirect
from pyha.models import Collection, Request
from pyha.roles import HANDLER_SENS, USER, HANDLER_ANY, HANDLER_COLL
import requests


def _get_authentication_info(request, token):
    url = settings.LAJIAUTH_URL + "token/" + token
    response = requests.get(url)
    if response.status_code != 200:
        return None
    else:
        content = json.loads(response.content.decode('utf-8'))
        return content

def log_in(request, content, token):
    if not "user_id" in request.session:
        request.session["user_id"] = content["user"]["qname"]
        request.session["user_name"] = content["user"]["name"]
        request.session["user_email"] = content["user"]["email"]
        request.session["user_roles"] = []
        for r in content["user"]["roles"]:
            if HANDLER_SENS in r:
                request.session["user_roles"].append(r)
        request.session["token"] = token
        if not "_language" in request.session:
           request.session["_language"] = "fi"
        add_collection_owner(request, content)
        if not HANDLER_SENS in request.session["user_roles"] or HANDLER_COLL in request.session["user_roles"]:
           request.session["user_roles"] = [USER]
           request.session["current_user_role"] = USER
        else:
           request.session["user_roles"].append(USER)
           request.session["user_roles"].append(HANDLER_ANY)
           request.session["current_user_role"] = HANDLER_ANY
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

def authenticate(request, token):
    '''
    Logs user in if the token is valid.
    :param request: A HttpRequest to create session for
    :param token: The token returned by LajiAuth.
    :return: true if user is authenticated succesfully
    '''
    result = _get_authentication_info(request, token)
    if result is None:
        return False
    else:
        log_in(request, result, token)
        return True

def authenticated(request):
    '''
    Checks if user is authenticated if MOCK_AUTHENTICATION is set to 'Skip', always returns true,
    :param request:
    :return:
    '''
    if settings.MOCK_AUTHENTICATION == "Skip": return True
    else :return "user_id" in request.session

def get_user_name(request):
    if "user_name" in request.session:
        return request.session["user_name"]

def add_collection_owner(request, content):
    if Collection.objects.filter(downloadRequestHandler__contains=request.session["user_id"]).count() > 0:	
        request.session["user_roles"].append(HANDLER_COLL)
        
def logged_in(request):
    if "user_id" in request.session:
        return True
    return False

def _process_auth_response(request, indexpath):
    if not "token" in request.POST:
        return HttpResponseRedirect(settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next='+str(indexpath))
    if authenticate(request, request.POST["token"]):
        return HttpResponseRedirect('/pyha/'+indexpath)
    else:
        return HttpResponseRedirect(settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next='+str(indexpath))
        
def is_allowed_to_view(request, requestId):
    userId = request.session["user_id"]
    role1 = HANDLER_SENS in request.session.get("user_roles", [None])
    role2 = HANDLER_COLL in request.session.get("user_roles", [None])
    return allowed_to_view(request, requestId, userId, role1, role2)

def allowed_to_view(request, requestId, userId, role1, role2):
    if HANDLER_ANY in request.session.get("current_user_role", [None]):
            if not Request.requests.filter(id=requestId, status__gt=0).exists():
                return False
            if role2 and not role1:
                if not Collection.objects.filter(request=requestId, customSecured__gt = 0, downloadRequestHandler__contains = str(userId), status__gt=0).count() > 0:
                    return False
    else:
            if not Request.requests.filter(id=requestId, user=userId, status__gte=0).exists():
                return False
    return True
    
def is_allowed_to_handle(request, target, requestId):
    if target == 'sens':
        return HANDLER_SENS in request.session["user_roles"]
    elif Collection.objects.filter(request=requestId, address=target).exists():
        collection = Collection.objects.get(request=requestId, address=target)
        return request.session["user_id"] in collection.downloadRequestHandler
    return False
