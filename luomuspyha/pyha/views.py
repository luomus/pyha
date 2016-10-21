import json
import os
import requests
from luomuspyha import secrets
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
			return _process_auth_response(request,'')
		userEmail = request.session["user_email"]
		request_list = Request.requests.filter(email=userEmail).order_by('-date')
		context = {"email": request.session["user_email"], "title": "Tervetuloa", "maintext": "Tervetuloa!", "requests": request_list, "static": settings.STA_URL }
		return render(request, 'pyha/index.html', context)

def login(request):
		return _process_auth_response(request, '')

def logout(request):
		if not logged_in(request):
			return _process_auth_response(request, '')
		context = {"title": "Kirjaudu ulos", "message": "Kirjauduit ulos onnistuneesti", "static": settings.STA_URL}
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
			return HttpResponseRedirect('/pyha/'+indexpath)
		else:
			return HttpResponseRedirect(settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next='+str(indexpath))

def receiver(request):
		if 'JSON' in request.POST:
                        text = request.POST['JSON']
                        jsond = text
                        store(jsond)
		else:
			jsond = request.body.decode("utf-8")
			store(jsond)
		return HttpResponse('')


def jsonmock(request):
		return render(request, 'pyha/mockjson.html')

def show_request(request):
		requestNum = os.path.basename(os.path.normpath(request.path))
		if not logged_in(request):
			return _process_auth_response(request, "request/"+requestNum)
		userEmail = request.session["user_email"]
		if not Request.requests.filter(order=requestNum, email=userEmail).exists():
                        return HttpResponseRedirect('pyha/')
		userRequest = Request.requests.get(order=requestNum, email=userEmail)
		filterList = json.loads(userRequest.filter_list, object_hook=lambda d: Namespace(**d))
		collectionList = Collection.objects.filter(request=userRequest.id)
		for i, c in enumerate(collectionList):
                        c.result = requests.get(settings.LAJIAPI_URL+str(c)+"?lang=fi&access_token="+secrets.TOKEN).json()
                        

		filterResultList = list(range(len(vars(filterList).keys())))
		for i, b in enumerate(vars(filterList).keys()):
			tup = (b, getattr(filterList, b))
			filterResultList[i] = tup
		context = {"email": request.session["user_email"], "userRequest": userRequest, "filters": filterResultList, "collections": collectionList, "static": settings.STA_URL }
		if(userRequest.status == 0):
                    return render(request, 'pyha/requestform.html', context)
		else:
                    return render(request, 'pyha/requestview.html', context)

def change_description(request):
	if request.method == 'POST':
		next = request.POST.get('next', '/')
		requestId = request.POST.get('requestid')
		userRequest = Request.requests.get(id = requestId)
		userRequest.description = request.POST.get('description')
		userRequest.save(update_fields=['description'])
		return HttpResponseRedirect(next)

def approve(request):
	if request.method == 'POST':
		requestId = request.POST.get('requestid')
		requestedCollections = request.POST.getlist('checkb');
		if(len(requestedCollections) > 0):
			for i in requestedCollections:
				userCollection = Collection.objects.get(collection_id = i, request = requestId)
				userCollection.status = 1
				userCollection.save(update_fields=['status'])
			collectionList = Collection.objects.filter(request=requestId, status = 0)
			collectionList.delete()
			userRequest = Request.requests.get(id = requestId)
			userRequest.status = 1
			userRequest.save(update_fields=['status'])
	return HttpResponseRedirect('/pyha/')
