import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, Context, RequestContext
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.conf import settings
from pyha.login import authenticate
from pyha.login import log_out

@require_http_methods(["GET"])
def index(request):	
        if not logged_in(request):
                return _process_auth_response(request)
        context = {"title": "Tervetuloa " + request.session["user_name"] , "message": "Kaytat sahkopostiosoitetta: " + request.session["user_email"], "target_header":"Valitsemasi rajaukset: ", "targets": ['linnut','nisakkaat'], "collection_header":"Tarvitsemasi aineistot: ", "collections": ['ain1', 'ain2', 'ain3']}
        return render(request, 'pyha/index.html', context)

def login(request):      
	return _process_auth_response(request)

def logout(request):
        if not logged_in(request):
                return _process_auth_response(request)
        context = {"title": "Kirjaudu ulos", "message": "Kirjauduit ulos onnistuneesti"}
        log_out(request)
        return render(request, 'pyha/index.html', context)

def logged_in(request):
        if "user_id" in request.session:
                return True
        return False

def _process_auth_response(request):
    if not "token" in request.POST:
        return HttpResponseRedirect(settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next')
    if authenticate(request, request.POST["token"]):
        return HttpResponseRedirect('pyha/index')
    else:
        return HttpResponseRedirect(settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next')

def receiver(request):

        print(request)
        #data = json.loads(request.body)
        #filters = data['filters']
        #collections = data ['collections']
        return HttpResponse('')
   
def jsonmock(request):
         return render(request, 'pyha/mockjson.html')
	
