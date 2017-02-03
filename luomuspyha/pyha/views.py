import json
import os
import requests
import ast
import time
from luomuspyha import secrets
from argparse import Namespace
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.http import JsonResponse
from django.template import loader, Context, RequestContext
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.conf import settings
from pyha.login import authenticate
from pyha.login import log_out
from requests.auth import HTTPBasicAuth
from pyha.email import fetch_email_address
from pyha.warehouse import store
from pyha.models import Collection, Request, RequestLogEntry, RequestChatEntry, RequestInformationChatEntry, ContactPreset, RequestContact
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from itertools import chain
from itertools import groupby
from pyha.roles import *
from pyha.email import *
from django.core.cache import cache
from datetime import datetime, timedelta

@csrf_exempt
def index(request):
		if check_language(request):
			return HttpResponseRedirect(request.path)
		if not logged_in(request):
			return _process_auth_response(request,'')
		userId = request.session["user_id"]
		lang = request.LANGUAGE_CODE
		hasRole = HANDLER_SENS in request.session.get("user_roles", [None]) or HANDLER_COLL in request.session.get("user_roles", [None])
		if HANDLER_ANY in request.session.get("current_user_role", [None]):
			request_list = []
			if HANDLER_SENS in request.session.get("user_roles", [None]):
				request_list += Request.requests.exclude(status__lte=0).filter(id__in=Collection.objects.filter(taxonSecured__gt = 0).exclude(downloadRequestHandler__contains = str(userId)).values("request")).order_by('-date')
			if HANDLER_COLL in request.session.get("user_roles", [None]):
				request_list += Request.requests.exclude(status__lte=0).filter(id__in=Collection.objects.filter(customSecured__gt = 0,downloadRequestHandler__contains = str(userId),status__gt = 0 ).values("request")).order_by('-date')
			request_list = list(set(request_list))
			for r in request_list:
				r.email =fetch_email_address(r.user)
			context = {"role": hasRole, "email": request.session["user_email"], "requests": request_list, "static": settings.STA_URL }
			return render(request, 'pyha/handler/index.html', context)
		else:
			request_list = Request.requests.filter(user=userId, status__gte=0).order_by('-date')
			context = {"role": hasRole, "email": request.session["user_email"], "requests": request_list, "static": settings.STA_URL }
			return render(request, 'pyha/index.html', context)

def logout(request):
		if not logged_in(request):
			return _process_auth_response(request, '')
		log_out(request)
		return HttpResponseRedirect("https://beta.laji.fi/")

def logged_in(request):
		if "user_id" in request.session:
			return True
		return False

def change_role(request):
		if not logged_in(request) and not 'role' in request.POST:
			return HttpResponse('/')
		next = request.POST.get('next', '/pyha/')
		request.session['current_user_role'] = request.POST['role']
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
			req = store(jsond)
		else:
			jsond = request.body.decode("utf-8")
			req = store(jsond)
		if(req):
			send_mail_after_receiving_request(req.id, req.lang)
		return HttpResponse('')

@csrf_exempt
def download(request, link):
		if request.method == 'POST':
			userRequest = Request.requests.get(lajiId=link)
			userRequest.status = 8
			userRequest.downloadDate = datetime.now()
			userRequest.save()
			send_mail_after_receiving_download(userRequest.id)
		return HttpResponse('')

def jsonmock(request):
		return render(request, 'pyha/mockjson.html')
		
def check_language(request):
		if request.GET.get('lang'):
				request.session["_language"] = request.GET.get('lang')
				return True
		return False


def allowed_to_view(request, userRequest, userId, role1, role2):
		if HANDLER_ANY in request.session.get("current_user_role", [None]):
				if not Request.requests.filter(id=userRequest.id, status__gt=0).exists():
					return False
				if role2 and not role1:
					if not Collection.objects.filter(request=userRequest.id, customSecured__gt = 0, downloadRequestHandler__contains = str(userId), status__gt=0).count() > 0:
						return False
				if(userRequest.status == 0):
					return False
		else:
				if not Request.requests.filter(id=userRequest.id, user=userId, status__gte=0).exists():
					return False
		if(userRequest.status == -1):
				return False
		return True

@csrf_exempt
def show_request(request):
		if check_language(request):
			return HttpResponseRedirect(request.path)
		#Has Access
		requestId = os.path.basename(os.path.normpath(request.path))
		if not logged_in(request):
			return _process_auth_response(request, "request/"+requestId)
		userRequest = Request.requests.get(id=requestId)
		userId = request.session["user_id"]
		userRole = request.session["current_user_role"]
		role1 = HANDLER_SENS in request.session.get("user_roles", [None])
		role2 = HANDLER_COLL in request.session.get("user_roles", [None])
		if not allowed_to_view(request, userRequest, userId, role1, role2):
			return HttpResponseRedirect('/pyha/')
		#make a log entry
		if userRequest.user != userId:
			make_logEntry_view(request, userRequest, userId, role1, role2)
		context = create_request_view_context(requestId, request, userRequest, userId, role1, role2)
		if HANDLER_ANY in request.session.get("current_user_role", [None]):
			return render(request, 'pyha/handler/requestview.html', context)
		else:
			if(userRequest.status == 0):
				result = render(request, 'pyha/requestform.html', context)
				'''result['Cache-Control'] = 'no-cache, no-store, must-revalidate'
				result['Pragma'] = 'no-cache'
				result['Expires'] = '0'''
				return result
			else:
				return render(request, 'pyha/requestview.html', context)

def make_logEntry_view(request, userRequest, userId, role1, role2):
	if not "has_viewed" in request.session:
		request.session["has_viewed"] = []
	if userRequest.id not in request.session.get("has_viewed", [None]):
		logRole = USER
		if role1:
			logRole = HANDLER_SENS
			if role2:
				logRole = HANDLER_BOTH 
		elif role2:
			logRole = HANDLER_COLL
		request.session["has_viewed"].append(userRequest.id)
		RequestLogEntry.requestLog.create(request=userRequest, user=userId, 
		role=logRole, action=RequestLogEntry.VIEW)

def show_filters(request, userRequest):
		filterList = json.loads(userRequest.filter_list, object_hook=lambda d: Namespace(**d))
		filterResultList = list(range(len(vars(filterList).keys())))
		lang = request.LANGUAGE_CODE
		if 'has expired' in cache.get('filters'+str(userRequest.id)+lang, 'has expired'):
			filters = requests.get(settings.LAJIFILTERS_URL)
			if(filters.status_code == 200):
				filtersobject = json.loads(filters.text, object_hook=lambda d: Namespace(**d))
				for i, b in enumerate(vars(filterList).keys()):
					languagelabel = b
					filternamelist = getattr(filterList, b)
					if isinstance(filternamelist, str):
						stringlist = []
						value = getattr(filterList, b)
						value = translate_truth(value, lang)
						stringlist.append(value)
						filternamelist = stringlist
					if b in filters.json():
						filterfield = getattr(filtersobject, b)
						label = getattr(filterfield, "label")
						if(lang == 'sw'):
							languagelabel = getattr(label, "sv")
						else:
							languagelabel = getattr(label, request.LANGUAGE_CODE)
						if "RESOURCE" in getattr(filterfield, "type"):
							resource = getattr(filterfield, "resource")
							for k, a in enumerate(getattr(filterList, b)):
								if resource.startswith("metadata"):
									filterfield2 = requests.get(settings.LAJIAPI_URL+str(resource)+"/?lang=" + request.LANGUAGE_CODE + "&access_token="+secrets.TOKEN)
									filtername = str(a)
									for ii in filterfield2.json():
										if (str(a) == ii['id']):
											filtername = ii['value']
											break
								else:
									if(lang == 'sw'):
										filterfield2 = requests.get(settings.LAJIAPI_URL+str(resource)+"/"+str(a)+"?lang=sv&access_token="+secrets.TOKEN)
									else:
										filterfield2 = requests.get(settings.LAJIAPI_URL+str(resource)+"/"+str(a)+"?lang=" + request.LANGUAGE_CODE + "&access_token="+secrets.TOKEN)
									filternameobject = json.loads(filterfield2.text, object_hook=lambda d: Namespace(**d))
									filtername = getattr(filternameobject, "name", str(a))
								filternamelist[k]= filtername
						if "ENUMERATION" in getattr(filterfield, "type"):
							enumerations = getattr(filterfield, "enumerations")
							for k, e in enumerate(getattr(filterList, b)):
								filtername = e
								for n in enumerations:
									if e == getattr(n, "name"):
										if(lang == 'sw'):
											filtername = getattr(n.label, "sv")
										else:
											filtername = getattr(n.label, lang)
										break
								filternamelist[k]= filtername
					tup = (b, filternamelist, languagelabel)
					filterResultList[i] = tup
				cache.set('filters'+str(userRequest.id)+lang,filterResultList)
			else:
				for i, b in enumerate(vars(filterList).keys()):
					languagelabel = b
					filternamelist = getattr(filterList, b)
					if isinstance(filternamelist, str):
						stringlist = []
						value = getattr(filterList, b)
						value = translate_truth(value, lang)
						stringlist.append(value)
						filternamelist = stringlist
					tup = (b, filternamelist, b)
					filterResultList[i] = tup
				return filterResultList
		else:
			return cache.get('filters'+str(userRequest.id)+lang)
		return filterResultList

def translate_truth(value, lang):
		if value == "true":
			if(lang == 'fi'):
				value = "Kyllä"
			if(lang == 'en'):
				value = "Yes"
			if(lang == 'sw'):
				value = "Ja"
		elif value == "false":
			if(lang == 'fi'):
				value = "Ei"
			if(lang == 'en'):
				value = "No"
			if(lang == 'sw'):
				value = "Nej"
		return value

def show_reasons(userRequest):
		reasonlist = json.loads(userRequest.reason, object_hook=lambda d: Namespace(**d))
		fields = reasonlist.fields
		tuplist = []
		for f in fields.__dict__:
			t = (f,getattr(fields, f))
			tuplist.append(t)
		reasonlist.fields = tuplist
		return reasonlist

def show_request_contacts(userRequest):
		contacts = []
		contact = {}
		contact["personName"] = userRequest.personName
		contact["personStreetAddress"] = userRequest.personStreetAddress
		contact["personPostOfficeName"] = userRequest.personPostOfficeName
		contact["personPostalCode"] = userRequest.personPostalCode
		contact["personCountry"] = userRequest.personCountry
		contact["personEmail"] = userRequest.personEmail
		contact["personPhoneNumber"] = userRequest.personPhoneNumber
		contact["personOrganizationName"] = userRequest.personOrganizationName
		contact["personCorporationId"] = userRequest.personCorporationId
		contacts.append(contact)
		contactlist = RequestContact.objects.filter(request=userRequest)
		for c in contactlist:
			contacts.append(c)
		return contacts

def requestLog(request, requestId):
		requestLog_list = list(RequestLogEntry.requestLog.filter(request=requestId).order_by('-date'))
		collectionList = []
		email = []
		for l in requestLog_list:
			if(l.collection):
				collectionList.append(l.collection)
			l.email = fetch_email_address(l.user)
			l.name = fetch_user_name(l.user)
		get_values_for_collections(requestId, request, collectionList)
		for l in requestLog_list:
			if(l.collection):
				collectionList.append(l)
		return requestLog_list
		
def requestChat(request, requestId):
		requestChat_list = list(RequestChatEntry.requestChat.filter(request=requestId).order_by('date'))
		email = []
		for l in requestChat_list:
			l.name = fetch_user_name(l.user)
		return requestChat_list

def requestInformationChat(request, requestId):
		requestChat_list = list(RequestInformationChatEntry.requestInformationChat.filter(request=requestId).order_by('date'))
		email = []
		for l in requestChat_list:
			l.name = fetch_user_name(l.user)
		return requestChat_list

def create_coordinates(userRequest):
		filterList = json.loads(userRequest.filter_list, object_hook=lambda d: Namespace(**d))
		coord = getattr(filterList,"coordinates", None)
		if(coord):
			coordinates = coord[0].split(":", 5)
			return coordinates
		return None


def create_request_view_context(requestId, request, userRequest, userId, role1, role2):
		taxonList = []
		customList = []
		collectionList = []
		lang = request.LANGUAGE_CODE
		create_collections_for_lists(requestId, request, taxonList, customList, collectionList, userRequest, userId, role1, role2)
		taxon = False
		for collection in collectionList:
			collection.allSecured = collection.customSecured + collection.taxonSecured
			if(collection.taxonSecured > 0):
				taxon = True
		hasRole = role1 or role2
		request_owner = fetch_user_name(userRequest.user)
		request_owners_email = fetch_email_address(userRequest.user)
		context = {"taxonlist": taxonList, "customlist": customList, "taxon": taxon, "role": hasRole, "role1": role1, "role2": role2, "email": request.session["user_email"], "userRequest": userRequest, "requestLog_list": requestLog(request, requestId), "filters": show_filters(request, userRequest), "collections": collectionList, "static": settings.STA_URL, "request_owner": request_owner, "request_owners_email": request_owners_email}
		if userRequest.status > 0:
			context["coordinates"] = create_coordinates(userRequest)
			context["next"] = next = request.GET.get('next', 'request')
			context["contactlist"] = show_request_contacts(userRequest)
			context["reasonlist"] = show_reasons(userRequest)
			context["endable"] = Collection.objects.filter(request=userRequest.id,taxonSecured__gt=0, customSecured=0).exists() or Collection.objects.filter(request=userRequest.id,status=4).exists()
		if userRequest.status == 8:
			lang = request.LANGUAGE_CODE
			if(lang == 'sw'):
				languagelabel = getattr(label, "sv")
			context["download"] = settings.LAJIDOW_URL+userRequest.lajiId+'?personToken='+userId
			context["downloadable"] = datetime.strptime(userRequest.downloadDate, "%Y-%m-%d %H:%M:%S.%f") > datetime.now()-timedelta(days=30)
		if userRequest.status == 0 and Request.requests.filter(user=userId,status__gte=1).count() > 0:
			context["old_request"] = ContactPreset.objects.get(user=userId)
		else:
			context["requestChat_list"] = requestChat(request, requestId)
			requestInformationChat_list = requestInformationChat(request, requestId)
			context["requestInformationChat_list"] = requestInformationChat_list
			if(requestInformationChat_list):
				context["information"] = not requestInformationChat_list[-1].question
		return context

def get_values_for_collections(requestId, request, List):
		for i, c in enumerate(List):
			if 'has expired' in cache.get(str(c)+'collection_values'+request.LANGUAGE_CODE, 'has expired'):
				c.result = requests.get(settings.LAJIAPI_URL+"collections/"+str(c)+"?lang=" + request.LANGUAGE_CODE + "&access_token="+secrets.TOKEN).json()
				cache.set(str(c)+'collection_values'+request.LANGUAGE_CODE, c.result)
			else:
				c.result = cache.get(str(c)+'collection_values'+request.LANGUAGE_CODE)
				r = c.result
				c.result["collectionName"] = c.result.get("collectionName",c.address)
				c.result["description"] = c.result.get("description","-")

def create_collections_for_lists(requestId, request, taxonList, customList, collectionList, userRequest, userId, role1, role2):
		hasCollection = False
		collectionList += Collection.objects.filter(request=userRequest.id, status__gte=0)
		if HANDLER_ANY in request.session.get("current_user_role", [None]):
			if role1:
				taxonList += Collection.objects.filter(request=userRequest.id, taxonSecured__gt = 0, status__gte=0)
				hasCollection = True
			customList += Collection.objects.filter(request=userRequest.id, customSecured__gt = 0, status__gte=0)
			hasCollection = True
		if not hasCollection:
			taxonList += Collection.objects.filter(request=userRequest.id, taxonSecured__gt = 0, status__gte=0)
			customList += Collection.objects.filter(request=userRequest.id, customSecured__gt = 0, status__gte=0)
		get_values_for_collections(requestId, request, collectionList)
		get_values_for_collections(requestId, request, customList)
		get_values_for_collections(requestId, request, taxonList)

def change_description(request):
	if request.method == 'POST':
		next = request.POST.get('next', '/')
		requestId = request.POST.get('requestid')
		userRequest = Request.requests.get(id = requestId)
		userRequest.description = request.POST.get('description')
		userRequest.save(update_fields=['description'])
	return HttpResponseRedirect(next)

#removes sensitive sightings
def remove_sensitive_data(request):
	if request.method == 'POST':
		next = request.POST.get('next', '/')
		collectionId = request.POST.get('collectionId')
		requestId = request.POST.get('requestid')
		collection = Collection.objects.get(id = collectionId)
		collection.taxonSecured = 0;
		collection.save(update_fields=['taxonSecured'])
		if(collection.customSecured == 0) and (collection.status != -1):
			collection.status = -1
			collection.save(update_fields=['status'])
			check_all_collections_removed(requestId)
		return HttpResponseRedirect(next)

#removes custom sightings
def remove_custom_data(request):
	next = request.POST.get('next', '/')
	if request.method == 'POST':
		collectionId = request.POST.get('collectionId')
		requestId = request.POST.get('requestid')
		collection = Collection.objects.get(id = collectionId)
		collection.customSecured = 0;
		collection.save(update_fields=['customSecured'])
		if(collection.taxonSecured == 0) and (collection.status != -1):
			collection.status = -1
			collection.save(update_fields=['status'])
			check_all_collections_removed(requestId)
		return HttpResponseRedirect(next)
	return HttpResponseRedirect(next)

def remove_ajax(request):
	if request.method == 'POST' and request.POST.get('requestid'):
		if check_language(request):
				return HttpResponseRedirect(request.path)
		#Has Access
		requestId = request.POST.get('requestid')
		if not logged_in(request):
			return _process_auth_response(request, "request/"+requestId)
		userRequest = Request.requests.get(id=requestId)
		userId = request.session["user_id"]
		userRole = request.session["current_user_role"]
		role1 = HANDLER_SENS in request.session.get("user_roles", [None])
		role2 = HANDLER_COLL in request.session.get("user_roles", [None])
		
		if not allowed_to_view(request, userRequest, userId, role1, role2):
			return HttpResponse('/pyha/', status=310)
		collectionId = request.POST.get('collectionId')
		requestId = request.POST.get('requestid')
		userRequest = Request.requests.get(id = requestId)
		collection = Collection.objects.get(id = collectionId)
		collection.taxonSecured = 0;
		collection.customSecured = 0;
		collection.save(update_fields=['taxonSecured', 'customSecured'])
		if(collection.customSecured == 0) and (collection.status != -1):
			collection.status = -1
			collection.save(update_fields=['status'])
			if(check_all_collections_removed(requestId)):
				return HttpResponse("/pyha/", status=310)
		context = create_request_view_context(requestId, request, userRequest, userId, role1, role2)
		return HttpResponse("")
	return HttpResponse("")
	
def get_taxon(request):
	if request.method == 'POST' and request.POST.get('requestid'):
		if check_language(request):
				return HttpResponseRedirect(request.path)
		#Has Access
		requestId = request.POST.get('requestid')
		if not logged_in(request):
			return HttpResponse("/pyha/", status=310)
		userRequest = Request.requests.get(id=requestId)
		userId = request.session["user_id"]
		userRole = request.session["current_user_role"]
		role1 = HANDLER_SENS in request.session.get("user_roles", [None])
		role2 = HANDLER_COLL in request.session.get("user_roles", [None])
		
		if not allowed_to_view(request, userRequest, userId, role1, role2):
			return HttpResponse("/pyha/", status=310)
		context = create_request_view_context(requestId, request, userRequest, userId, role1, role2)
		return render(request, 'pyha/requestformtaxon.html', context)
	return HttpResponse("/pyha/", status=310)
	
def get_custom(request):
	if request.method == 'POST' and request.POST.get('requestid'):
		if check_language(request):
				return HttpResponseRedirect(request.path)
		#Has Access
		requestId = request.POST.get('requestid')
		if not logged_in(request):
			return _process_auth_response(request, "request/"+requestId)
		userRequest = Request.requests.get(id=requestId)
		userId = request.session["user_id"]
		userRole = request.session["current_user_role"]
		role1 = HANDLER_SENS in request.session.get("user_roles", [None])
		role2 = HANDLER_COLL in request.session.get("user_roles", [None])
		
		if not allowed_to_view(request, userRequest, userId, role1, role2):
			return HttpResponseRedirect('/pyha/')
		context = create_request_view_context(requestId, request, userRequest, userId, role1, role2)
		return render(request, 'pyha/requestformcustom.html', context)
	return HttpResponse("")
	
def get_summary(request):
	if request.method == 'POST' and request.POST.get('requestid'):
		if check_language(request):
				return HttpResponseRedirect(request.path)
		#Has Access
		requestId = request.POST.get('requestid')
		if not logged_in(request):
			return _process_auth_response(request, "request/"+requestId)
		userRequest = Request.requests.get(id=requestId)
		userId = request.session["user_id"]
		userRole = request.session["current_user_role"]
		role1 = HANDLER_SENS in request.session.get("user_roles", [None])
		role2 = HANDLER_COLL in request.session.get("user_roles", [None])
		
		if not allowed_to_view(request, userRequest, userId, role1, role2):
			return HttpResponseRedirect('/pyha/')
		context = create_request_view_context(requestId, request, userRequest, userId, role1, role2)
		return render(request, 'pyha/requestformsummary.html', context)
	return HttpResponse("")
	
def create_contact(request):
	if request.method == 'POST' and request.POST.get('requestid') and request.POST.get('id'):
		if check_language(request):
				return HttpResponseRedirect(request.path)
		#Has Access
		requestId = request.POST.get('requestid')
		if not logged_in(request):
			return _process_auth_response(request, "request/"+requestId)
		userRequest = Request.requests.get(id=requestId)
		userId = request.session["user_id"]
		userRole = request.session["current_user_role"]
		role1 = HANDLER_SENS in request.session.get("user_roles", [None])
		role2 = HANDLER_COLL in request.session.get("user_roles", [None])
		
		if not allowed_to_view(request, userRequest, userId, role1, role2):
			return HttpResponseRedirect('/pyha/')
		context = create_request_view_context(requestId, request, userRequest, userId, role1, role2)
		context["contact_id"] = request.POST.get('id');
		return render(request, 'pyha/requestformcontact.html', context)
	return HttpResponse("")

def description_ajax(request):
	if request.method == 'POST' and request.POST.get('requestid'):
		if request.method == 'POST':
			next = request.POST.get('next', '/')
			requestId = request.POST.get('requestid')
			userRequest = Request.requests.get(id = requestId)
			userRequest.description = request.POST.get('description')
			userRequest.save(update_fields=['description'])
			return HttpResponseRedirect(next)
		return render(request, 'pyha/requestformcustom.html', context)
	return HttpResponse("")
	
def get_request_header(request):
	if request.method == 'POST' and request.POST.get('requestid'):
		if check_language(request):
				return HttpResponseRedirect(request.path)
		#Has Access
		requestId = request.POST.get('requestid')
		if not logged_in(request):
			return _process_auth_response(request, "request/"+requestId)
		userRequest = Request.requests.get(id=requestId)
		userId = request.session["user_id"]
		userRole = request.session["current_user_role"]
		role1 = HANDLER_SENS in request.session.get("user_roles", [None])
		role2 = HANDLER_COLL in request.session.get("user_roles", [None])
		
		if not allowed_to_view(request, userRequest, userId, role1, role2):
			return HttpResponseRedirect('/pyha/')
		context = create_request_view_context(requestId, request, userRequest, userId, role1, role2)
		return render(request, 'pyha/requestheader.html', context)
	return HttpResponse("")
	
def fetch_user_name(personId):
	'''
	fetches user name for a person registered in Laji.fi
	:param personId: person identifier 
	:returns: person's full name
	'''
	username = 'pyha'
	password = settings.LAJIPERSONAPI_PW 
	if 'has expired' in cache.get('name'+personId, 'has expired'):
		response = requests.get(settings.LAJIPERSONAPI_URL+personId+"?format=json", auth=HTTPBasicAuth(username, password ))
		if(response.status_code == 200):
			data = response.json()
			name = data['rdf:RDF']['MA.person']['MA.fullName']
			cache.set('name'+personId,name)
			return name
		else:
			cache.set('name'+personId,personId)
			return personId
	else:
		return cache.get('name'+personId)


def removeCollection(request):
	if request.method == 'POST':
		requestId = request.POST.get('requestid')
		collectionId = request.POST.get('collectionid')
		redirect_path = request.POST.get('next')
		collection = Collection.objects.get(address = collectionId, request = requestId)
		#avoid work when submitted multiple times
		if(collection.status != -1):
			collection.status = -1
			collection.save(update_fields=['status'])
			check_all_collections_removed(requestId)
		return HttpResponseRedirect(redirect_path)



#check if all collections have status -1. If so set status of request to -1.
def check_all_collections_removed(requestId):
		userRequest = Request.requests.get(id = requestId)
		collectionList = userRequest.collection_set.filter(status__gte=0 )
		if not collectionList:
			userRequest.status = -1
			userRequest.save(update_fields=['status'])
			return True
		return False

def approve(request):
	if request.method == 'POST':
		lang = 'fi' #ainakin toistaiseksi
		requestId = request.POST.get('requestid')
		userRequest = Request.requests.get(id = requestId)
		requestedCollections = request.POST.getlist('checkb');
		senschecked = request.POST.get('checkbsens');
		if(userRequest.status == 0 and senschecked):
			for rc in requestedCollections:
				userCollection = Collection.objects.get(address = rc, request = requestId)
				if userCollection.status == 0:
					userCollection.status = 1
					userCollection.save(update_fields=['status'])
			for c in Collection.objects.filter(request = requestId):
				if c.status == 0:
					c.customSecured = 0
					if userRequest.sensstatus == 0:
						c.taxonsecured = 0
					c.save(update_fields=['customSecured'])
					if c.taxonSecured == 0:
						c.status = -1
						c.save(update_fields=['status'])
				#postia vain niille aineistoille, joilla on aineistokohtaisesti salattuja tietoja
				if(c.customSecured > 0):
					send_mail_for_approval(requestId, c, lang)

			for count in range(2, count_contacts(request.POST)+1):
				create_new_contact(request, userRequest, count)

			userRequest.reason = create_argument_blob(request)
			userRequest.status = 1
			if senschecked:
				userRequest.sensstatus = 1
			userRequest.personName = request.POST.get('request_person_name_1')
			userRequest.personStreetAddress = request.POST.get('request_person_street_address_1')
			userRequest.personPostOfficeName = request.POST.get('request_person_post_office_name_1')
			userRequest.personPostalCode = request.POST.get('request_person_postal_code_1')
			userRequest.personCountry = request.POST.get('request_person_country_1')
			userRequest.personEmail = request.POST.get('request_person_email_1')
			userRequest.personPhoneNumber = request.POST.get('request_person_phone_number_1')
			userRequest.personOrganizationName = request.POST.get('request_person_organization_name_1')
			userRequest.personCorporationId = request.POST.get('request_person_corporation_id_1')
			userRequest.save()
			update_contact_preset(request, userRequest)
			if userRequest.sensstatus == 1:
				send_mail_for_approval_sens(requestId, lang)
			#make a log entry
			RequestLogEntry.requestLog.create(request=userRequest, user=request.session["user_id"], role=USER, action=RequestLogEntry.ACCEPT)
	return HttpResponseRedirect('/pyha/')

def count_contacts(post):
	i = 0
	for string in post:
		if "request_person_name" in string:
			i += 1
	return i

def create_new_contact(request, userRequest, count):
	contact = RequestContact()
	contact.request = userRequest
	contact.personName = request.POST.get('request_person_name_'+str(count))
	contact.personStreetAddress = request.POST.get('request_person_street_address_'+str(count))
	contact.personPostOfficeName = request.POST.get('request_person_post_office_name_'+str(count))
	contact.personPostalCode = request.POST.get('request_person_postal_code_'+str(count))
	contact.personCountry = request.POST.get('request_person_country_'+str(count))
	contact.personEmail = request.POST.get('request_person_email_'+str(count))
	contact.personPhoneNumber = request.POST.get('request_person_phone_number_'+str(count))
	contact.personOrganizationName = request.POST.get('request_person_organization_name_'+str(count))
	contact.personCorporationId = request.POST.get('request_person_corporation_id_'+str(count))
	contact.save()

def create_argument_blob(request):
	post = request.POST
	data = {}
	data['argument_choices'] = post.getlist('argument_choices')
	fields = {}
	for string in post:
		if "argument_" in string and not "argument_choices" in string:
			fields[string] = post.get(string)
	data['fields'] = fields
	return json.dumps(data)

def update_contact_preset(request, userRequest):
		contactPreset = ContactPreset.objects.filter(user=userRequest.user).first()
		if contactPreset is None:
			contactPreset = ContactPreset()
		contactPreset.user = userRequest.user
		contactPreset.requestPersonName = request.POST.get('request_person_name_1')
		contactPreset.requestPersonStreetAddress = request.POST.get('request_person_street_address_1')
		contactPreset.requestPersonPostOfficeName = request.POST.get('request_person_post_office_name_1')
		contactPreset.requestPersonPostalCode = request.POST.get('request_person_postal_code_1')
		contactPreset.requestPersonCountry = request.POST.get('request_person_country_1')
		contactPreset.requestPersonEmail = request.POST.get('request_person_email_1')
		contactPreset.requestPersonPhoneNumber = request.POST.get('request_person_phone_number_1')
		contactPreset.requestPersonOrganizationName = request.POST.get('request_person_organization_name_1')
		contactPreset.requestPersonCorporationId = request.POST.get('request_person_corporation_id_1')
		contactPreset.save()

def answer(request):
		next = request.POST.get('next', '/')
		if request.method == 'POST':
			collectionId = request.POST.get('collectionid')
			requestId = request.POST.get('requestid')
			userRequest = Request.requests.get(id = requestId)
			if(int(request.POST.get('answer')) == 2):
				newChatEntry = RequestInformationChatEntry()
				newChatEntry.request = Request.requests.get(id=requestId)
				newChatEntry.date = datetime.now()
				newChatEntry.user = request.session["user_id"]
				newChatEntry.question = True
				newChatEntry.message = request.POST.get('reason')
				newChatEntry.save()
				userRequest.status = 6
				userRequest.save()
				send_mail_after_additional_information_requested(requestId, request.LANGUAGE_CODE)
			elif "sens" not in collectionId:
				collection = Collection.objects.get(request=requestId, address=collectionId)
				if (request.session["user_id"] in collection.downloadRequestHandler) and userRequest.status != 7 and userRequest.status != 8 and userRequest.status != 3:
					if (int(request.POST.get('answer')) == 1):
						collection.status = 4
						#make a log entry
						RequestLogEntry.requestLog.create(request = Request.requests.get(id = requestId), collection = collection, user = request.session["user_id"], role = HANDLER_COLL, action =RequestLogEntry.DECISION_POSITIVE)
					else:
						collection.status = 3
						#make a log entry
						RequestLogEntry.requestLog.create(request = Request.requests.get(id = requestId),collection = collection, user = request.session["user_id"], role = HANDLER_COLL, action =RequestLogEntry.DECISION_NEGATIVE)
					collection.decisionExplanation = request.POST.get('reason')
					collection.save()
					update(requestId, request.LANGUAGE_CODE)
			elif HANDLER_SENS in request.session["user_roles"]:
				if (int(request.POST.get('answer')) == 1):
					userRequest.sensstatus = 4
					#make a log entry
					RequestLogEntry.requestLog.create(request = Request.requests.get(id = requestId), user = request.session["user_id"], role = HANDLER_SENS, action = RequestLogEntry.DECISION_POSITIVE)
				else:
					userRequest.sensstatus = 3
					#make a log entry
					RequestLogEntry.requestLog.create(request = Request.requests.get(id = requestId), user = request.session["user_id"], role = HANDLER_SENS, action = RequestLogEntry.DECISION_NEGATIVE)
				userRequest.sensDecisionExplanation = request.POST.get('reason')
				userRequest.save()
				update(requestId, request.LANGUAGE_CODE)
		return HttpResponseRedirect(next)

def information(request):
		next = request.POST.get('next', '/')
		if request.method == 'POST':
			requestId = request.POST.get('requestid')
			if(int(request.POST.get('information')) == 2):
				newChatEntry = RequestInformationChatEntry()
				newChatEntry.request = Request.requests.get(id=requestId)
				newChatEntry.date = datetime.now()
				newChatEntry.user = request.session["user_id"]
				newChatEntry.question = False
				newChatEntry.message = request.POST.get('reason')
				newChatEntry.save()
				userRequest = Request.requests.get(id = requestId)
				userRequest.status = 1
				userRequest.save()
				update(requestId, request.LANGUAGE_CODE)
		return HttpResponseRedirect(next)

def comment_sensitive(request):
		next = request.POST.get('next', '/')
		if request.method == 'POST':
			message = request.POST.get('commentsForAuthorities')
			requestId = request.POST.get('requestid')
			if HANDLER_SENS in request.session["user_roles"]:
				newChatEntry = RequestChatEntry()
				newChatEntry.request = Request.requests.get(id=requestId)
				newChatEntry.date = datetime.now()
				newChatEntry.user = request.session["user_id"]
				newChatEntry.message = message
				newChatEntry.save()
		return HttpResponseRedirect(next)

def update(requestId, lang):
		#for both sensstatus and collection status
		#status 0: Ei sensitiivistä tietoa
		#status 1: Odottaa aineiston toimittajan käsittelyä
		#status 2: Osittain hyväksytty
		#status 3: Hylätty
		#status 4: Hyväksytty
		#status 6: Odottaa vastausta lisäkysymyksiin
		#status 7: Odottaa latauksen valmistumista
		#status 8: Ladattava
		wantedRequest = Request.requests.get(id=requestId)
		#tmp variable for checking if status changed
		statusBeforeUpdate = wantedRequest.status
		requestCollections = Collection.objects.filter(request=requestId)
		accepted = 0
		colaccepted = 0
		declined = 0
		pending = 0
		if wantedRequest.status != 6:
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
					colaccepted += 1
					accepted += 1
			if wantedRequest.sensstatus == 3:
				wantedRequest.status = 3
			elif (accepted >= 0 and pending > 0) and declined == 0:
				wantedRequest.status = 1
			elif (accepted > 0 and declined > 0) and pending == 0:
				wantedRequest.status = 2
				if colaccepted > 0:
					send_download_request(requestId)
			elif (pending == 0 and accepted == 0) and declined > 0:
				wantedRequest.status = 3
			elif accepted > 0 and (declined == 0 and pending == 0):
				wantedRequest.status = 4
				if colaccepted > 0:
					send_download_request(requestId)
			elif declined > 0:
				wantedRequest.status = 1
			else:
				wantedRequest.status = 5
			wantedRequest.save()
		
		emailsOnUpdate(requestCollections, wantedRequest, lang, statusBeforeUpdate)

def send_download_request(requestId):
		payload = {}
		userRequest = Request.requests.get(id=requestId)
		payload["id"] = userRequest.lajiId
		payload["personId"] = userRequest.user
		collectionlist = Collection.objects.filter(request=userRequest, status=4)
		if userRequest.sensstatus == 4:
			additionlist = Collection.objects.filter(request=userRequest, customSecured=0, taxonSecured__gt=0)
			collectionlist = list(chain(collectionlist, additionlist))
		cname = []
		for c in collectionlist:
			cname.append(c.address)
		payload["approvedCollections"] = cname
		payload["sensitiveApproved"] = "true"
		payload["secured"] = "true"
		payload["downloadFormat"] = "CSV_FLAT"
		payload["access_token"] = secrets.TOKEN
		filters = json.loads(userRequest.filter_list, object_hook=lambda d: Namespace(**d))
		for f in filters.__dict__:
			payload[f] = getattr(filters, f)
		response = requests.post(settings.LAJIAPI_URL+"warehouse/private-query/downloadApproved", data=payload)

def initialize_download(request):
		next = request.POST.get('next', '/')
		if request.method == 'POST':
			requestId = request.POST.get('requestid')
			userRequest = Request.requests.get(id=requestId)
			if (userRequest.status == 4 or userRequest.status == 2 or userRequest.sensstatus == 4):
				send_download_request(requestId)
				userRequest.status = 7
				userRequest.save()
		return HttpResponseRedirect(next)

"""
	Send "request has been handled" email 
	IF request.sensstatus is 0(no sensitive information) OR 3(declined) OR 4(accepted)  
	AND 
	all it's collections have status != 1(waiting for approval)
"""
def emailsOnUpdate(requestCollections, userRequest, lang, statusBeforeUpdate):
	#count collections that are still waiting for approval
	collectionsNotHandled = len(requestCollections)
	for c in requestCollections:
		if c.status != 1:
			collectionsNotHandled -=1
	#check if request is handled
	if collectionsNotHandled == 0 and (userRequest.sensstatus == 3 or userRequest.sensstatus == 4 or userRequest.sensstatus ==0):
		send_mail_after_request_has_been_handled_to_requester(userRequest.id, lang)
	elif(statusBeforeUpdate!=userRequest.status):
		#Send email if status changed
		send_mail_after_request_status_change_to_requester(userRequest.id, lang)











