from argparse import Namespace
from datetime import timedelta, datetime
from itertools import chain
import json
from django.core.cache import caches
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseRedirect
from pyha.email import send_mail_after_request_has_been_handled_to_requester, send_mail_after_request_status_change_to_requester
from pyha.login import logged_in, _process_auth_response, is_allowed_to_view, is_request_owner
from pyha.models import RequestLogEntry, RequestSensitiveChatEntry, RequestHandlerChatEntry, RequestInformationChatEntry, ContactPreset, RequestContact, Collection, Request, StatusEnum, Sens_StatusEnum,\
	Col_StatusEnum
from pyha.roles import HANDLER_ANY, CAT_HANDLER_SENS, CAT_HANDLER_COLL, CAT_HANDLER_BOTH, USER, ADMIN, CAT_ADMIN
from pyha.utilities import filterlink
from pyha.warehouse import get_values_for_collections, send_download_request, fetch_user_name, fetch_role, fetch_email_address, show_filters, create_coordinates, get_result_for_target, get_collections_where_download_handler, update_collections
from pyha.log_utils import changed_by_session_user, changed_by

#removes sensitive sightings
def remove_sensitive_data(request):
	if request.method == 'POST':
		if not logged_in(request):
			return _process_auth_response(request, "pyha")
		requestId = request.POST.get('requestid')
		if not is_request_owner(request, requestId):
			return HttpResponseRedirect(reverse('pyha:root'))
		nextRedirect = request.POST.get('next', '/')
		collectionId = request.POST.get('collectionId')
		collection = Collection.objects.get(id = collectionId)
		collection.taxonSecured = 0
		collection.changedBy = changed_by_session_user(request)
		collection.save()
		if(collection.customSecured == 0) and (collection.status != -1):
			collection.status = -1
			collection.changedBy = changed_by_session_user(request)
			collection.save()
			check_all_collections_removed(requestId)
		return HttpResponseRedirect(nextRedirect)
	return HttpResponseRedirect(reverse('pyha:root'))

#removes custom sightings
def remove_custom_data(request):
	if request.method == 'POST':
		if not logged_in(request):
			return _process_auth_response(request, "pyha")
		requestId = request.POST.get('requestid')
		if not is_request_owner(request, requestId):
			return HttpResponseRedirect(reverse('pyha:root'))
		nextRedirect = request.POST.get('next', '/')
		collectionId = request.POST.get('collectionId')
		collection = Collection.objects.get(id = collectionId)
		collection.customSecured = 0
		collection.changedBy = changed_by_session_user(request)
		collection.save()
		if(collection.taxonSecured == 0) and (collection.status != -1):
			collection.status = StatusEnum.DISCARDED
			collection.changedBy = changed_by_session_user(request)
			collection.save()
			check_all_collections_removed(requestId)
		return HttpResponseRedirect(nextRedirect)
	return HttpResponseRedirect(reverse('pyha:root'))


def removeCollection(request):
	if request.method == 'POST':
		if not logged_in(request):
			return _process_auth_response(request, "pyha")
		requestId = request.POST.get('requestid', '?')
		if not is_request_owner(request, requestId):
			return HttpResponseRedirect(reverse('pyha:root'))
		nextRedirect = request.POST.get('next', '/')
		collectionId = request.POST.get('collectionid')
		collection = Collection.objects.get(address = collectionId, request = requestId)
		#avoid work when submitted multiple times
		if(collection.status != -1):
			collection.status = -1
			collection.changedBy = changed_by_session_user(request)
			collection.save()
			check_all_collections_removed(requestId)
		return HttpResponseRedirect(nextRedirect)
	return HttpResponseRedirect(reverse('pyha:root'))

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
	
def create_collection_for_list(request, collectionList, userRequest):
	collectionList += Collection.objects.filter(request=userRequest.id, status__gte=0)
	get_values_for_collections(userRequest.id, request, collectionList)
	
def get_all_secured(userRequest):
	allSecured = 0
	collectionList = Collection.objects.filter(request=userRequest.id, status__gte=0)
	for collection in collectionList:
		collection.allSecured = collection.customSecured + collection.taxonSecured
		allSecured += collection.allSecured
	return allSecured
	

#check if all collections have status -1. If so set status of request to -1.
def check_all_collections_removed(requestId):
	userRequest = Request.objects.get(id = requestId)
	collectionList = userRequest.collection_set.filter(status__gte=0)
	if not collectionList:
		userRequest.status = -1
		userRequest.changedBy = changed_by("pyha")
		userRequest.save()
		return True
	return False

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
	contact.changedBy = changed_by_session_user(request)
	contact.save()

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
	contactPreset.changedBy = changed_by_session_user(request)
	contactPreset.save()

def target_valid(target, requestId):
	if target == 'sens' or target == 'admin':
		return True
	elif Collection.objects.filter(request=requestId, address=target).exists():
		return True
	return False

def handlers_cannot_be_updated():
	return not update_collection_handlers()
	
def update_collection_handlers():	
	if 'has expired' in caches['collections'].get('collection_update', 'has expired'):
		if update_collections():
			return True
		else:
			return False
	return True

def count_unhandled_requests(userId):
	role = fetch_role(userId)
	unhandled = set()
	if(settings.TUN_URL+CAT_HANDLER_SENS in role):
		request_list = Request.objects.exclude(status__lte=0).filter(sensStatus = Sens_StatusEnum.WAITING)
		for r in request_list:
			if (r.status == StatusEnum.WAITING):
				#if(RequestLogEntry.requestLog.filter(request = r.id, user = userId, action = 'VIEW').count() == 0):
				#	unhandled.add(r)
				#else:
				questioning = False
				if RequestInformationChatEntry.requestInformationChat.filter(request=r.id, target='sens').count() > 0 and r.sensStatus == Sens_StatusEnum.WAITING:
					chat = RequestInformationChatEntry.requestInformationChat.filter(request=r.id, target='sens').order_by('-date')[0]
					if chat.question:
						questioning = True
				if not questioning:
					unhandled.add(r)
	q = Request.objects.exclude(status__lte=0)
	c0 = q.filter(id__in=Collection.objects.filter(customSecured__gt = 0, address__in = get_collections_where_download_handler(userId), status = StatusEnum.WAITING).values("request")).exclude(sensStatus=Sens_StatusEnum.IGNORE_OFFICIAL)
	c1 = q.filter(id__in=Collection.objects.filter(address__in = get_collections_where_download_handler(userId), status = StatusEnum.WAITING).values("request"), sensStatus=Sens_StatusEnum.IGNORE_OFFICIAL)
	request_list = chain(c0, c1)
	for r in request_list:
		if (r.status == StatusEnum.WAITING):
			#if(RequestLogEntry.requestLog.filter(request = r.id, user = userId, action = 'VIEW').count() == 0):
			#	unhandled.add(r)
			#else:
			questioning = False
			for co in get_collections_where_download_handler(userId):
				if RequestInformationChatEntry.requestInformationChat.filter(request=r.id, target = co).count() > 0 and Collection.objects.get(request=r.id, address=co).status == StatusEnum.WAITING:
					cochat = RequestInformationChatEntry.requestInformationChat.filter(request=r.id, target = co).order_by('-date')[0]
					if cochat.question:
						questioning = True
						break
			if not questioning:
				unhandled.add(r)
	return len(unhandled)

def update_request_status(userRequest, lang):
	if(not userRequest.status in [StatusEnum.WAITING_FOR_DOWNLOAD, StatusEnum.DOWNLOADABLE]):
		if userRequest.sensStatus == Sens_StatusEnum.IGNORE_OFFICIAL:
			ignore_official_database_update_request_status(userRequest, lang) 
		else: 
			database_update_request_status(userRequest, lang)
			
def database_update_request_status(wantedRequest, lang):

	statusBeforeUpdate = wantedRequest.status
	requestCollections = Collection.objects.filter(request=wantedRequest.id, status__gte=0)
	taxon = False
	for collection in requestCollections:
		if(collection.taxonSecured > 0):
			taxon = True
			break
	accepted = 0
	colaccepted = 0
	declined = 0
	pending = 0
	if taxon:
		if wantedRequest.status != StatusEnum.WAITING_FOR_INFORMATION:
			if wantedRequest.sensStatus == Sens_StatusEnum.WAITING:
				pending += 1
			elif wantedRequest.sensStatus == Sens_StatusEnum.REJECTED:
				declined += 1
			elif wantedRequest.sensStatus == Sens_StatusEnum.APPROVED:
				accepted += 1
			for c in requestCollections:
				if c.status == StatusEnum.WAITING:
					pending += 1
				elif c.status == StatusEnum.REJECTED:
					declined += 1
				elif c.status == StatusEnum.APPROVED:
					colaccepted += 1
					accepted += 1
			if wantedRequest.sensStatus == Sens_StatusEnum.REJECTED:
				wantedRequest.status = StatusEnum.REJECTED
			elif (accepted >= 0 and pending > 0) and declined == 0:
				wantedRequest.status = StatusEnum.WAITING
			elif (accepted > 0 and declined > 0) and pending == 0:
				wantedRequest.status = StatusEnum.PARTIALLY_APPROVED
				if colaccepted > 0:
					send_download_request(wantedRequest.id)
					wantedRequest.status = StatusEnum.WAITING_FOR_DOWNLOAD
			elif (pending == 0 and accepted == 0) and declined > 0:
				wantedRequest.status = StatusEnum.REJECTED
			elif accepted > 0 and (declined == 0 and pending == 0):
				wantedRequest.status = StatusEnum.APPROVED
				if colaccepted > 0:
					send_download_request(wantedRequest.id)
					wantedRequest.status = StatusEnum.WAITING_FOR_DOWNLOAD
			elif pending > 0:
				wantedRequest.status = StatusEnum.WAITING
			else:
				wantedRequest.status = StatusEnum.UNKNOWN
			wantedRequest.changedBy = changed_by("pyha")
			wantedRequest.save()
	else:
		for c in requestCollections:
			if c.status == StatusEnum.WAITING:
				pending += 1
			elif c.status == StatusEnum.REJECTED:
				declined += 1
			elif c.status == StatusEnum.APPROVED:
				colaccepted += 1
				accepted += 1
		if (accepted >= 0 and pending > 0) and declined == 0:
			if wantedRequest.status != StatusEnum.WAITING_FOR_INFORMATION:
				wantedRequest.status = StatusEnum.WAITING
		elif (accepted > 0 and declined > 0) and pending == 0:
			wantedRequest.status = StatusEnum.PARTIALLY_APPROVED
			if colaccepted > 0:
				send_download_request(wantedRequest.id)
				wantedRequest.status = StatusEnum.WAITING_FOR_DOWNLOAD
		elif (pending == 0 and accepted == 0) and declined > 0:
			wantedRequest.status = StatusEnum.REJECTED
		elif accepted > 0 and (declined == 0 and pending == 0):
			wantedRequest.status = StatusEnum.APPROVED
			if colaccepted > 0:
				send_download_request(wantedRequest.id)
				wantedRequest.status = StatusEnum.WAITING_FOR_DOWNLOAD
		elif pending > 0:
			wantedRequest.status = StatusEnum.WAITING
		else:
			wantedRequest.status = StatusEnum.UNKNOWN
		if(wantedRequest.status != statusBeforeUpdate):
			wantedRequest.changedBy = changed_by("pyha")
			wantedRequest.save()
			
	emailsOnUpdate(requestCollections, wantedRequest, lang, statusBeforeUpdate)
	
	
def ignore_official_database_update_request_status(wantedRequest, lang):

	statusBeforeUpdate = wantedRequest.status
	requestCollections = Collection.objects.filter(request=wantedRequest.id, status__gte=0)
	accepted = 0
	colaccepted = 0
	declined = 0
	pending = 0
	for c in requestCollections:
		if c.status == StatusEnum.WAITING:
			pending += 1
		elif c.status == StatusEnum.REJECTED:
			declined += 1
		elif c.status == StatusEnum.APPROVED:
			colaccepted += 1
			accepted += 1
	if (accepted >= 0 and pending > 0) and declined == 0:
		if wantedRequest.status != StatusEnum.WAITING_FOR_INFORMATION:
			wantedRequest.status = StatusEnum.WAITING 
	elif (accepted > 0 and declined > 0) and pending == 0:
		wantedRequest.status = StatusEnum.PARTIALLY_APPROVED
		if colaccepted > 0:
			send_download_request(wantedRequest.id)
			wantedRequest.status = StatusEnum.WAITING_FOR_DOWNLOAD
	elif (pending == 0 and accepted == 0) and declined > 0:
		wantedRequest.status = StatusEnum.REJECTED
	elif accepted > 0 and (declined == 0 and pending == 0):
		wantedRequest.status = StatusEnum.APPROVED
		if colaccepted > 0:
			send_download_request(wantedRequest.id)
			wantedRequest.status = StatusEnum.WAITING_FOR_DOWNLOAD
	elif pending > 0:
		wantedRequest.status = StatusEnum.WAITING
	else:
		wantedRequest.status = StatusEnum.UNKNOWN
	if(wantedRequest.status != statusBeforeUpdate):
		wantedRequest.changedBy = changed_by("pyha")
		wantedRequest.save()
			
	emailsOnUpdate(requestCollections, wantedRequest, lang, statusBeforeUpdate)
		
def handler_waiting_status(r, request, userId):
	r.waitingstatus = 0
	if CAT_HANDLER_SENS in request.session.get("user_roles", [None]) and r.sensStatus == 1:
		r.waitingstatus = 1
	elif CAT_HANDLER_COLL in request.session.get("user_roles", [None]):
		#if Collection.objects.filter(request=r.id, customSecured__gt = 0, downloadRequestHandler__contains = str(userId), status = 1).exists():
		if Collection.objects.filter(request=r.id, customSecured__gt = 0, address__in = get_collections_where_download_handler(userId), status = 1).exists():
			r.waitingstatus = 1
	return

def handler_information_answered_status(r, request, userId):
	r.answerstatus = 0
	if CAT_HANDLER_SENS in request.session.get("user_roles", [None]):
		if RequestInformationChatEntry.requestInformationChat.filter(request=r.id, target='sens').count() > 0 and r.sensStatus == Sens_StatusEnum.WAITING:
			chat = RequestInformationChatEntry.requestInformationChat.filter(request=r.id, target='sens').order_by('-date')[0]
			if not chat.question:
				r.answerstatus = 1
	if CAT_HANDLER_COLL in request.session.get("user_roles", [None]):
		for co in get_collections_where_download_handler(userId):
			if RequestInformationChatEntry.requestInformationChat.filter(request=r.id, target = co).count() > 0 and Collection.objects.get(request=r.id, address=co).status == StatusEnum.WAITING:
				cochat = RequestInformationChatEntry.requestInformationChat.filter(request=r.id, target = co).order_by('-date')[0]
				if not cochat.question:
					r.answerstatus = 1
					break
	return

def create_request_view_context(requestId, request, userRequest):
	taxonList = []
	customList = []
	collectionList = []
	userId = request.session["user_id"]
	role1 = CAT_HANDLER_SENS in request.session.get("user_roles", [None])
	role2 = CAT_HANDLER_COLL in request.session.get("user_roles", [None])
	role3 = CAT_ADMIN in request.session.get("user_roles", [None])
	lang = request.LANGUAGE_CODE
	create_collections_for_lists(requestId, request, taxonList, customList, collectionList, userRequest, userId, role1, role2)
	taxon = False
	allSecured = 0
	for collection in collectionList:
		collection.allSecured = collection.customSecured + collection.taxonSecured
		allSecured += collection.allSecured
		if(collection.taxonSecured > 0):
			taxon = True
	hasRole = role1 or role2 or role3
	request_owner = fetch_user_name(userRequest.user)
	request_owners_email = fetch_email_address(userRequest.user)
	context = {"taxonlist": taxonList, "customlist": customList, "taxon": taxon, "role": hasRole, "role1": role1, "role2": role2, "email": request.session["user_email"], "userRequest": userRequest, "requestLog_list": requestLog(request, requestId), "filters": show_filters(request, userRequest), "collections": collectionList, "static": settings.STA_URL, "request_owner": request_owner, "request_owners_email": request_owners_email}
	context["coordinates"] = create_coordinates(userRequest)
	context["filter_link"] = filterlink(userRequest, settings.FILTERS_LINK)
	context["official_filter_link"] = filterlink(userRequest, settings.OFFICIAL_FILTERS_LINK)
	context["sensitivity_terms"] = "pyha/skipofficial/terms/skipofficial_collection-"+lang+".html" if userRequest.sensStatus == Sens_StatusEnum.IGNORE_OFFICIAL else "pyha/official/terms/sensitivity-"+lang+".html"
	context["username"] = request.session["user_name"]
	context["allSecured"] = allSecured
	if role2: context["handles"] = get_collections_where_download_handler(userId)
	if userRequest.status > 0:
		context["next"] = request.GET.get('next', 'history')
		context["contactlist"] = get_request_contacts(userRequest)
		context["reasonlist"] = get_reasons(userRequest)
		if(userRequest.sensStatus == Sens_StatusEnum.IGNORE_OFFICIAL):
			isEndable = (Collection.objects.filter(request=userRequest.id,status=4).exists())
		else:
			isEndable = (Collection.objects.filter(request=userRequest.id, taxonSecured__gt=0, customSecured=0).exists() or Collection.objects.filter(request=userRequest.id,status=4).exists()) and (not taxon or userRequest.sensStatus == Sens_StatusEnum.APPROVED)		
		context["endable"] = isEndable
		context["user"] = userId
		handler_waiting_status(userRequest, request, userId)
	if userRequest.status == 8:
		context["download"] = settings.LAJIDOW_URL+userRequest.lajiId+'?personToken='+request.session["token"]
		context["downloadable"] = datetime.strptime(userRequest.downloadDate, "%Y-%m-%d %H:%M:%S.%f") > datetime.now()-timedelta(days=60)
	if userRequest.status == 0 and Request.objects.filter(user=userId,status__gte=1).count() > 0:
		context["contactPreset"] = ContactPreset.objects.get(user=userId)
	else:
		context["requestSensitiveChat_list"] = requestSensitiveChat(userRequest)
		context["requestHandlerChat_list"] = requestHandlerChat(request, userRequest)
		requestInformationChat_list = requestInformationChat(request, userRequest, role1, role2, userId)
		context["requestInformationChat_list"] = requestInformationChat_list
		if(requestInformationChat_list):
			context["information"] = not requestInformationChat_list[-1].question
	return context

def get_request_contacts(userRequest):
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

def get_reasons(userRequest):
	if(userRequest.reason != None):
		reasonlist = json.loads(userRequest.reason, object_hook=lambda d: Namespace(**d))
		fields = reasonlist.fields
		tuplist = []
		for f in fields.__dict__:
			t = (f,getattr(fields, f))
			tuplist.append(t)
		reasonlist.fields = tuplist
		return reasonlist
	return None

def make_logEntry_view(request, userRequest, userId, role1, role2, role3):
	if not "has_viewed" in request.session:
		request.session["has_viewed"] = []
	if userRequest.id not in request.session.get("has_viewed", [None]):
		logRole = USER
		if role3:
			logRole = CAT_ADMIN
		elif role1:
			logRole = CAT_HANDLER_SENS
			if role2:
				logRole = CAT_HANDLER_BOTH 
		elif role2:
			logRole = CAT_HANDLER_COLL
		request.session["has_viewed"].append(userRequest.id)
		RequestLogEntry.requestLog.create(request=userRequest, user=userId, role=logRole, action=RequestLogEntry.VIEW)
		

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

def requestSensitiveChat(userRequest):
		requestSensitiveChat_list = list(RequestSensitiveChatEntry.requestChat.filter(request=userRequest).order_by('date'))
		for c in requestSensitiveChat_list:
			c.name = fetch_user_name(c.user)
		return requestSensitiveChat_list
	
def requestHandlerChat(request, userRequest):
		requestHandlerChat_list = list(RequestHandlerChatEntry.requestHandlerChat.filter(request=userRequest).order_by('date'))
		for c in requestHandlerChat_list:
			c.name = fetch_user_name(c.user)
			get_result_for_target(request, c)
		return requestHandlerChat_list

def requestInformationChat(request, userRequest, role1, role2, userId):
		requestInformationChat_list = []
		if HANDLER_ANY in request.session.get("current_user_role", [None]):
			if role1:
				requestInformationChat_list += list(RequestInformationChatEntry.requestInformationChat.filter(request=userRequest, target='sens').order_by('date'))
			if role2:
				#for collection in Collection.objects.filter(request=requestId, customSecured__gt = 0, downloadRequestHandler__contains = str(userId)):
				if(userRequest.sensStatus != Sens_StatusEnum.IGNORE_OFFICIAL):
					for collection in Collection.objects.filter(request=userRequest, customSecured__gt = 0, address__in = get_collections_where_download_handler(userId)):
						requestInformationChat_list += list(RequestInformationChatEntry.requestInformationChat.filter(request=userRequest, target=str(collection)).order_by('date'))
				else:
					for collection in Collection.objects.filter(request=userRequest, address__in = get_collections_where_download_handler(userId)):
						requestInformationChat_list += list(RequestInformationChatEntry.requestInformationChat.filter(request=userRequest, target=str(collection)).order_by('date'))
		else:
			requestInformationChat_list += list(RequestInformationChatEntry.requestInformationChat.filter(request=userRequest).order_by('date'))
		for l in requestInformationChat_list:
			get_result_for_target(request, l)
		for l in requestInformationChat_list:
			l.name = fetch_user_name(l.user)
		return requestInformationChat_list
	
def get_collections_waiting_atleast_days(days_to_subtract):
	return Collection.objects.filter(request__in=Request.objects.filter(id__in=RequestLogEntry.requestLog.filter(action=RequestLogEntry.ACCEPT, date__lt = datetime.today() - timedelta(days=days_to_subtract)).values("request"), status=StatusEnum.WAITING, frozen=False), status = Col_StatusEnum.WAITING)

def is_collection_waiting_atleast_days(days_to_subtract, collection):
	return Request.objects.filter(id=collection.request.id, status=StatusEnum.WAITING, frozen=True).count() > 0 and Collection.objects.filter(id = collection.id, status = Col_StatusEnum.WAITING).count() > 0 and RequestLogEntry.requestLog.filter(request=collection.request, action=RequestLogEntry.ACCEPT, date__lt = datetime.today() - timedelta(days=days_to_subtract)).count() > 0

def contains_approved_collection(requestId):
	return Collection.objects.filter(request=requestId, status = Col_StatusEnum.APPROVED).count() > 0

"""
	Send "request has been handled" email 
	IF request.sensStatus is 0(no sensitive information) OR 3(declined) OR 4(accepted)  
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
	if collectionsNotHandled == 0 and (userRequest.sensStatus == 3 or userRequest.sensStatus == 4 or userRequest.sensStatus == 0):
		send_mail_after_request_has_been_handled_to_requester(userRequest.id, lang)
	elif(statusBeforeUpdate!=userRequest.status):
		#Send email if status changed
		send_mail_after_request_status_change_to_requester(userRequest.id, lang)








