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
		userId = request.session["user_id"]
		request_list = Request.requests.filter(user=userId, status__gte=0).order_by('-date')
		lang = request.LANGUAGE_CODE

		if(lang == 'fi'):
			title = 'Tervetuloa'
		elif(lang == 'en'):
			title = "Welcome"
		else:
			title = "Välkommen"
		context = {"email": request.session["user_email"], "title": title, "maintext": title  + "!", "requests": request_list, "static": settings.STA_URL }
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
		userId = request.session["user_id"]
		if not Request.requests.filter(order=requestNum, user=userId, status__gte=0).exists():
                        return HttpResponseRedirect('/pyha/')
		userRequest = Request.requests.get(order=requestNum, user=userId)
		filterList = json.loads(userRequest.filter_list, object_hook=lambda d: Namespace(**d))
		collectionList = Collection.objects.filter(request=userRequest.id, status__gte=0)
		for i, c in enumerate(collectionList):
                        c.result = requests.get(settings.LAJIAPI_URL+str(c)+"?lang=" + request.LANGUAGE_CODE + "&access_token="+secrets.TOKEN).json()
                        

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

def removeCollection(request):
	if request.method == 'POST':
		requestId = request.POST.get('requestid')
		collectionId = request.POST.get('collectionid')
		redirect_path = request.POST.get('next')
		print("Deleting collection:")
		print("request_id: " + requestId)
		print("collection_id: " + collectionId)
		collection = Collection.objects.get(collection_id = collectionId, request = requestId)
		collection.status = -1
		collection.save()
		#check if all collections have status -1. If so set status of request to -1.
		userRequest = Request.requests.get(id = requestId)
		collectionList = userRequest.collection_set.filter(status__gte=0 )
		if not collectionList:
			userRequest.status = -1
			userRequest.save()
			print("set request status to -1")
			return HttpResponseRedirect('/pyha/')
		else:
			return HttpResponseRedirect(redirect_path)

def approve(request):
	if request.method == 'POST':
		requestId = request.POST.get('requestid')
		requestedCollections = request.POST.getlist('checkb');
		if(len(requestedCollections) > 0):
			for i in requestedCollections:
				userCollection = Collection.objects.get(collection_id = i, request = requestId)
				userCollection.status = 1
				userCollection.save(update_fields=['status'])
			userRequest = Request.requests.get(id = requestId)
			userRequest.status = 1
			userRequest.save(update_fields=['status'])
	return HttpResponseRedirect('/pyha/')
