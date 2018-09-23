﻿from argparse import Namespace
from datetime import timedelta, datetime
import json

from django.conf import settings
from django.http import HttpResponseRedirect
from pyha.email import send_mail_after_request_has_been_handled_to_requester, send_mail_after_request_status_change_to_requester
from pyha.login import logged_in, _process_auth_response, is_allowed_to_view
from pyha.models import RequestLogEntry, RequestChatEntry, RequestInformationChatEntry, ContactPreset, RequestContact, Collection, Request
from pyha.roles import HANDLER_ANY, HANDLER_SENS, HANDLER_COLL, HANDLER_BOTH, USER
from pyha.utilities import filterlink
from pyha.warehouse import get_values_for_collections, send_download_request, fetch_user_name, fetch_email_address, show_filters, create_coordinates, get_result_for_target


#removes sensitive sightings
def remove_sensitive_data(request):
	if request.method == 'POST':
		if not logged_in(request):
			return _process_auth_response(request, "pyha")
		nextRedirect = request.POST.get('next', '/')
		collectionId = request.POST.get('collectionId')
		requestId = request.POST.get('requestid')
		collection = Collection.objects.get(id = collectionId)
		collection.taxonSecured = 0
		collection.save(update_fields=['taxonSecured'])
		if(collection.customSecured == 0) and (collection.status != -1):
			collection.status = -1
			collection.save(update_fields=['status'])
			check_all_collections_removed(requestId)
		return HttpResponseRedirect(nextRedirect)
	return HttpResponseRedirect('/pyha/')

#removes custom sightings
def remove_custom_data(request):
	if request.method == 'POST':
		if not logged_in(request):
			return _process_auth_response(request, "pyha")
		nextRedirect = request.POST.get('next', '/')
		collectionId = request.POST.get('collectionId')
		requestId = request.POST.get('requestid')
		collection = Collection.objects.get(id = collectionId)
		collection.customSecured = 0
		collection.save(update_fields=['customSecured'])
		if(collection.taxonSecured == 0) and (collection.status != -1):
			collection.status = -1
			collection.save(update_fields=['status'])
			check_all_collections_removed(requestId)
		return HttpResponseRedirect(nextRedirect)
	return HttpResponseRedirect('/pyha/')


def removeCollection(request):
	if request.method == 'POST':
		if not logged_in(request):
			return _process_auth_response(request, "pyha")
		requestId = request.POST.get('requestid', '?')
		if not is_allowed_to_view(request, requestId):
			return HttpResponseRedirect('/pyha/')
		collectionId = request.POST.get('collectionid')
		redirect_path = request.POST.get('next')
		collection = Collection.objects.get(address = collectionId, request = requestId)
		#avoid work when submitted multiple times
		if(collection.status != -1):
			collection.status = -1
			collection.save(update_fields=['status'])
			check_all_collections_removed(requestId)
		return HttpResponseRedirect(redirect_path)
	return HttpResponseRedirect("/pyha/")

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

#check if all collections have status -1. If so set status of request to -1.
def check_all_collections_removed(requestId):
	userRequest = Request.requests.get(id = requestId)
	collectionList = userRequest.collection_set.filter(status__gte=0)
	if not collectionList:
		userRequest.status = -1
		userRequest.save(update_fields=['status'])
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
	contactPreset.save()

def target_valid(request, target, requestId):
	if target == 'sens':
		return True
	elif Collection.objects.filter(request=requestId, address=target).exists():
		return True
	return False

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
	
	#for sensstatus
	#status 99: Ohitettu
	
	wantedRequest = Request.requests.get(id=requestId)
	#tmp variable for checking if status changed
	statusBeforeUpdate = wantedRequest.status
	requestCollections = Collection.objects.filter(request=requestId, status__gte=0)
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
	else:
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
		if (accepted >= 0 and pending > 0) and declined == 0:
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
		
def handler_waiting_status(r, request, userId):
	r.waitingstatus = 0
	if HANDLER_SENS in request.session.get("user_roles", [None]) and r.sensstatus == 1:
		r.waitingstatus = 1
	elif HANDLER_COLL in request.session.get("user_roles", [None]):
		for c in Collection.objects.filter(request=r.id, customSecured__gt = 0, downloadRequestHandler__contains = str(userId), status = 1):
			r.waitingstatus = 1
	return

def handler_information_answered_status(r, request, userId):
	r.answerstatus = 0
	if HANDLER_SENS in request.session.get("user_roles", [None]) and r.sensstatus == 1:
		if RequestInformationChatEntry.requestInformationChat.filter(request=r.id).exists():
			chat = RequestInformationChatEntry.requestInformationChat.filter(request=r.id).order_by('-date')[0]
			if not chat.question:
				r.answerstatus = 1
	return

def create_request_view_context(requestId, request, userRequest):
	taxonList = []
	customList = []
	collectionList = []
	userId = request.session["user_id"]
	role1 = HANDLER_SENS in request.session.get("user_roles", [None])
	role2 = HANDLER_COLL in request.session.get("user_roles", [None])
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
	context["coordinates"] = create_coordinates(userRequest)
	context["filter_link"] = filterlink(userRequest, request, context["filters"], settings.FILTERS_LINK)
	context["official_filter_link"] = filterlink(userRequest, request, context["filters"], settings.OFFICIAL_FILTERS_LINK)
	context["sensitivity_terms"] = "pyha/sensitivity/sensitivity-"+lang+".html"
	context["username"] = request.session["user_name"]
	if userRequest.status > 0:
		context["next"] = request.GET.get('next', 'history')
		context["contactlist"] = get_request_contacts(userRequest)
		context["reasonlist"] = get_reasons(userRequest)
		context["endable"] = (Collection.objects.filter(request=userRequest.id,taxonSecured__gt=0, customSecured=0).exists() or Collection.objects.filter(request=userRequest.id,status=4).exists()) and (not taxon or userRequest.sensstatus == 4)
		context["user"] = userId
		handler_waiting_status(userRequest, request, userId)
	if userRequest.status == 8:
		context["download"] = settings.LAJIDOW_URL+userRequest.lajiId+'?personToken='+request.session["token"]
		context["downloadable"] = datetime.strptime(userRequest.downloadDate, "%Y-%m-%d %H:%M:%S.%f") > datetime.now()-timedelta(days=30)
	if userRequest.status == 0 and Request.requests.filter(user=userId,status__gte=1).count() > 0:
		context["old_request"] = ContactPreset.objects.get(user=userId)
	else:
		context["requestChat_list"] = requestChat(request, requestId)
		requestInformationChat_list = requestInformationChat(request, requestId, role1, role2, userId)
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
	reasonlist = json.loads(userRequest.reason, object_hook=lambda d: Namespace(**d))
	fields = reasonlist.fields
	tuplist = []
	for f in fields.__dict__:
		t = (f,getattr(fields, f))
		tuplist.append(t)
	reasonlist.fields = tuplist
	return reasonlist

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
		for l in requestChat_list:
			l.name = fetch_user_name(l.user)
		return requestChat_list

def requestInformationChat(request, requestId, role1, role2, userId):
		requestChat_list = []
		if HANDLER_ANY in request.session.get("current_user_role", [None]):
			if role1:
				requestChat_list += list(RequestInformationChatEntry.requestInformationChat.filter(request=requestId, target='sens').order_by('date'))
			if role2:
				for collection in Collection.objects.filter(request=requestId, customSecured__gt = 0, downloadRequestHandler__contains = str(userId)):
					requestChat_list += list(RequestInformationChatEntry.requestInformationChat.filter(request=requestId, target=str(collection)).order_by('date'))
		else:
			requestChat_list += list(RequestInformationChatEntry.requestInformationChat.filter(request=requestId).order_by('date'))
		for l in requestChat_list:
			get_result_for_target(request, l)
		for l in requestChat_list:
			l.name = fetch_user_name(l.user)
		return requestChat_list


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







