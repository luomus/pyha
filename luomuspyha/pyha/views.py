import json
import os
from argparse import Namespace
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, Context, RequestContext
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.conf import settings
from pyha.login import authenticate
from pyha.login import log_out
from pyha.warehouse import store
from pyha.models import Collection, Request

def index(request):	
		if not logged_in(request):
			return _process_auth_response(request,'/pyha/')
		userEmail = request.session["user_email"]
		request_list = Request.requests.filter(email=userEmail)
		context = {"title": "Tervetuloa " + request.session["user_name"] , "message": "Kaytat sahkopostiosoitetta: " + request.session["user_email"], "requests": request_list }
		return render(request, 'pyha/index.html', context)

def login(request):      
		return _process_auth_response(request, '/pyha/')

def logout(request):
		if not logged_in(request):
			return _process_auth_response(request, '/pyha/')
		context = {"title": "Kirjaudu ulos", "message": "Kirjauduit ulos onnistuneesti"}
		log_out(request)
		return render(request, 'pyha/index.html', context)

def logged_in(request):
		if "user_id" in request.session:
			return True
		return False

def _process_auth_response(request, indexpath):
		if not "token" in request.POST:
			return HttpResponseRedirect(settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next='+str(indexpath))
		if authenticate(request, request.POST["token"]):
			return HttpResponseRedirect(indexpath)
		else:
			return HttpResponseRedirect(settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next='+str(indexpath))

def receiver(request):        
		if settings.MOCK_JSON:
			body = request.POST['JSON']     
		else:
			body = request.body          
		store(body)
		return HttpResponse('')

   
def jsonmock(request):
		return render(request, 'pyha/mockjson.html')
		
def show_request(request):
		if not logged_in(request):
			return _process_auth_response(request, request.path[1:])

		requestNum = os.path.basename(os.path.normpath(request.path))
		userEmail = request.session["user_email"]
		userRequest = Request.requests.get(order=requestNum, email=userEmail)
		x = json.loads(userRequest.filter_list, object_hook=lambda d: Namespace(**d))
		a = range(len(vars(x).keys()))
		for i, b in enumerate(vars(x).keys()):
			tup = (str(b), getattr(x, b))
			a[i] = tup
		context = {"title": userRequest.filter_list, "filters": a }
		return render(request, 'pyha/form.html', context)
