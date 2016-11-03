﻿import json
import os
import requests
import ast
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
from django.views.decorators.csrf import csrf_exempt, csrf_protect

@csrf_exempt
def index(request):
		if not logged_in(request):
			return _process_auth_response(request,'')
		userId = request.session["user_id"]
		lang = request.LANGUAGE_CODE

		if(lang == 'fi'):
			title = 'Tervetuloa'
		elif(lang == 'en'):
			title = "Welcome"
		else:
			title = "Välkommen"
		hasRole = False
		if secrets.ROLE_1 in request.session.get("user_roles", [None]):
                    hasRole = True
                    
		if secrets.ROLE_1 in request.session.get("user_role", [None]):
                    request_list = Request.requests.exclude(status=0).filter(id__in=Collection.objects.filter(secureReasons__icontains="taxon").values("request")).order_by('-date')
                    context = {"role": hasRole, "email": request.session["user_email"], "title": title, "maintext": title  + "!", "requests": request_list, "static": settings.STA_URL }
                    return render(request, 'pyha/role1/index.html', context)
		else:
                    request_list = Request.requests.filter(user=userId).order_by('-date')
                    context = {"role": hasRole, "email": request.session["user_email"], "title": title, "maintext": title  + "!", "requests": request_list, "static": settings.STA_URL }
                    return render(request, 'pyha/index.html', context)

def login(request):
		return _process_auth_response(request, '')

def logout(request):
		if not logged_in(request):
			return _process_auth_response(request, '')
		context = {"title": "Kirjaudu ulos", "message": "Kirjauduit ulos onnistuneesti", "static": settings.STA_URL}
		log_out(request)
		return HttpResponseRedirect("https://beta.laji.fi/")

def logged_in(request):
		if "user_id" in request.session:
			return True
		return False

def change_role(request):
		if not logged_in(request) and not 'role' in request.POST:
			return HttpResponse('/')
		next = request.POST.get('next', '/')
		request.session['user_role'] = request.POST['role']
		return HttpResponseRedirect(next)


def _process_auth_response(request, indexpath):
		if not "token" in request.POST:
			return HttpResponseRedirect(settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next='+str(indexpath))
		if authenticate(request, request.POST["token"]):
			return HttpResponseRedirect('/pyha/'+indexpath)
		else:
			return HttpResponseRedirect(settings.LAJIAUTH_URL+'login?target='+settings.TARGET+'&next='+str(indexpath))
@csrf_exempt
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
@csrf_exempt
def show_request(request):
		requestNum = os.path.basename(os.path.normpath(request.path))
		if not logged_in(request):
			return _process_auth_response(request, "request/"+requestNum)
		userId = request.session["user_id"]
		if not Request.requests.filter(order=requestNum, user=userId).exists():
			return HttpResponseRedirect('/pyha/')
		userRequest = Request.requests.get(order=requestNum, user=userId)
		filterList = json.loads(userRequest.filter_list, object_hook=lambda d: Namespace(**d))
		if secrets.ROLE_1 in request.session.get("user_role", [None]):
			collectionList = Collection.objects.filter(request=userRequest.id, secureReasons__icontains="taxon")
		else:
			collectionList = Collection.objects.filter(request=userRequest.id)
		for i, c in enumerate(collectionList):
			c.result = requests.get(settings.LAJIAPI_URL+"collections/"+str(c)+"?lang=" + request.LANGUAGE_CODE + "&access_token="+secrets.TOKEN).json()
			c.reasons = ast.literal_eval(c.secureReasons)

		taxon = False
		for collection in collectionList:
			if('DEFAULT_TAXON_CONSERVATION' in collection.reasons):
				taxon = True

		filters = requests.get(settings.LAJIFILTERS_URL)
		filtersobject = json.loads(filters.text, object_hook=lambda d: Namespace(**d))
		filterResultList = list(range(len(vars(filterList).keys())))
		for i, b in enumerate(vars(filterList).keys()):
			languagelabel = b
			filternamelist = getattr(filterList, b)
			if b in filters.json():
				filterfield = getattr(filtersobject, b)
				label = getattr(filterfield, "label")
				languagelabel = getattr(label, request.LANGUAGE_CODE)
				if "RESOURCE" in getattr(filterfield, "type"):
					resource = getattr(filterfield, "resource")
					for k, a in enumerate(getattr(filterList, b)):
						filterfield2 = requests.get(settings.LAJIAPI_URL+str(resource)+"/"+str(a)+"?lang="+request.LANGUAGE_CODE+"&access_token="+secrets.TOKEN)
						filternameobject = json.loads(filterfield2.text, object_hook=lambda d: Namespace(**d))
						filtername = getattr(filternameobject, "name")
						filternamelist[k]= filtername
			tup = (b, filternamelist, languagelabel)
			filterResultList[i] = tup

		hasRole = False
		if secrets.ROLE_1 in request.session.get("user_roles", [None]):
                        hasRole = True
		context = {"taxon": taxon, "role": hasRole, "email": request.session["user_email"], "userRequest": userRequest, "filters": filterResultList, "collections": collectionList, "static": settings.STA_URL }
                    
		if secrets.ROLE_1 in request.session.get("user_role", [None]):
                    return render(request, 'pyha/role1/requestview.html', context)
		else:
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
				if i not in "sens":
					userCollection = Collection.objects.get(collection_id = i, request = requestId)
					userCollection.status = 1
					userCollection.save(update_fields=['status'])
				else:
					userRequest = Request.requests.get(id = requestId)
					userRequest.sensstatus = 1
					userRequest.save(update_fields=['sensstatus'])
			collectionList = Collection.objects.filter(request=requestId, status = 0)
			collectionList.delete()
			userRequest = Request.requests.get(id = requestId)
			userRequest.status = 1
			userRequest.save(update_fields=['status'])
	return HttpResponseRedirect('/pyha/')

def answer(request):
		if request.method == 'POST':
			next = request.POST.get('next', '/')
			collectionId = request.POST.get('collectionid')
			requestId = request.POST.get('requestid')
			if "sens" not in collectionId:
				collection = Collection.objects.get(request=requestId, collection_id=collectionId)
				if (int(request.POST.get('answer')) == 1):  
					collection.status = 4
				else:
					collection.status = 3
				collection.decisionExplanation = request.POST.get('reason')
				collection.save()
				update(requestId)
			else:
				userRequest = Request.requests.get(id = requestId)
				if (int(request.POST.get('answer')) == 1):  
					userRequest.sensstatus = 4
				else:
					userRequest.sensstatus = 3
				userRequest.sensDecisionExplanation = request.POST.get('reason')
				userRequest.save()
				update(requestId)
		return HttpResponseRedirect(next)

def update(requestId):
		wantedRequest = Request.requests.get(id=requestId)
		requestCollections = Collection.objects.filter(request=requestId)
		accepted = 0
		declined = 0
		pending = 0
		if wantedRequest.sensstatus == 1:
			pending += 1
		elif wantedRequest.sensstatus == 2:
			accepted += 1
			declined += 1
		elif wantedRequest.sensstatus == 3:
			declined += 1
		elif wantedRequest.sensstatus == 4:
			accepted += 1
		for c in requestCollections:
			if c.status == 1:
				pending += 1
			elif c.status == 2:
				accepted += 1
				declined += 1
			elif c.status == 3:
				declined += 1
			elif c.status == 4:
				accepted += 1

		if accepted == 0 and declined == 0:
			wantedRequest.status = 1
		elif accepted > 0 and (declined > 0 or pending > 0):
			wantedRequest.status = 2
		elif accepted == 0 and declined > 0:
			wantedRequest.status = 3
		elif accepted > 0 and declined == 0:
			wantedRequest.status = 4
		else:
			wantedRequest.status = 5

		wantedRequest.save()
