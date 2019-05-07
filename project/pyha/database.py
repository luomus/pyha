import json
from argparse import Namespace
from datetime import timedelta, datetime
from itertools import chain
from django.core.cache import caches
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseRedirect
from django.template.loader import get_template
from pyha.email import send_mail_after_request_has_been_handled_to_requester, send_mail_after_request_status_change_to_requester, get_template_of_mail_for_approval, send_admin_mail_after_approved_request, send_admin_mail_after_approved_request_missing_handlers
from pyha.login import logged_in, _process_auth_response, is_allowed_to_view, is_request_owner
from pyha.models import RequestLogEntry, RequestSensitiveChatEntry, RequestHandlerChatEntry, RequestInformationChatEntry, ContactPreset, RequestContact, Collection, Request, StatusEnum, Sens_StatusEnum,\
	Col_StatusEnum, AdminUserSettings
from pyha.roles import HANDLER_ANY, CAT_HANDLER_SENS, CAT_HANDLER_COLL, CAT_HANDLER_BOTH, USER, ADMIN, CAT_ADMIN
from pyha.utilities import filterlink
from pyha.warehouse import get_values_for_collections, send_download_request, fetch_user_name, fetch_role, fetch_email_address, show_filters, create_coordinates, get_result_for_target, get_collections_where_download_handler, update_collections, get_download_handlers_with_collections_listed_for_collections, is_download_handler_in_collection
from pyha.log_utils import changed_by_session_user, changed_by
from pyha import toast


def remove_sensitive_data(http_request):
	if http_request.method == 'POST':
		if not logged_in(http_request):
			return _process_auth_response(http_request, "pyha")
		requestId = http_request.POST.get('requestid')
		if not is_request_owner(http_request, requestId):
			return HttpResponseRedirect(reverse('pyha:root'))
		nextRedirect = http_request.POST.get('next', '/')
		collectionId = http_request.POST.get('collectionId')
		collection = Collection.objects.get(id = collectionId)
		collection.taxonSecured = 0
		collection.changedBy = changed_by_session_user(http_request)
		collection.save()
		if(collection.customSecured == 0) and (collection.status != -1):
			collection.status = -1
			collection.changedBy = changed_by_session_user(http_request)
			collection.save()
			check_all_collections_removed(requestId)
		return HttpResponseRedirect(nextRedirect)
	return HttpResponseRedirect(reverse('pyha:root'))

def remove_custom_data(http_request):
	if http_request.method == 'POST':
		if not logged_in(http_request):
			return _process_auth_response(http_request, "pyha")
		requestId = http_request.POST.get('requestid')
		if not is_request_owner(http_request, requestId):
			return HttpResponseRedirect(reverse('pyha:root'))
		nextRedirect = http_request.POST.get('next', '/')
		collectionId = http_request.POST.get('collectionId')
		collection = Collection.objects.get(id = collectionId)
		collection.customSecured = 0
		collection.changedBy = changed_by_session_user(http_request)
		collection.save()
		if(collection.taxonSecured == 0) and (collection.status != -1):
			collection.status = StatusEnum.DISCARDED
			collection.changedBy = changed_by_session_user(http_request)
			collection.save()
			check_all_collections_removed(requestId)
		return HttpResponseRedirect(nextRedirect)
	return HttpResponseRedirect(reverse('pyha:root'))


def removeCollection(http_request):
	if http_request.method == 'POST':
		if not logged_in(http_request):
			return _process_auth_response(http_request, "pyha")
		requestId = http_request.POST.get('requestid', '?')
		if not is_request_owner(http_request, requestId):
			return HttpResponseRedirect(reverse('pyha:root'))
		nextRedirect = http_request.POST.get('next', '/')
		collectionId = http_request.POST.get('collectionid')
		collection = Collection.objects.get(address = collectionId, request = requestId)
		if(collection.status != -1):
			collection.status = -1
			collection.changedBy = changed_by_session_user(http_request)
			collection.save()
			check_all_collections_removed(requestId)
		return HttpResponseRedirect(nextRedirect)
	return HttpResponseRedirect(reverse('pyha:root'))

def create_collections_for_lists(requestId, http_request, taxonList, customList, collectionList, userRequest, userId, role1, role2):
	hasCollection = False
	collectionList += Collection.objects.filter(request=userRequest.id, status__gte=0)
	if HANDLER_ANY in http_request.session.get("current_user_role", [None]):
		if role1:
			taxonList += Collection.objects.filter(request=userRequest.id, taxonSecured__gt = 0, status__gte=0)
			hasCollection = True
		customList += Collection.objects.filter(request=userRequest.id, customSecured__gt = 0, status__gte=0)
		hasCollection = True
	if not hasCollection:
		taxonList += Collection.objects.filter(request=userRequest.id, taxonSecured__gt = 0, status__gte=0)
		customList += Collection.objects.filter(request=userRequest.id, customSecured__gt = 0, status__gte=0)
	get_values_for_collections(requestId, http_request, collectionList)
	get_values_for_collections(requestId, http_request, customList)
	get_values_for_collections(requestId, http_request, taxonList)
	
def create_collection_for_list(http_request, collectionList, userRequest):
	collectionList += Collection.objects.filter(request=userRequest.id, status__gte=0)
	get_values_for_collections(userRequest.id, http_request, collectionList)
	
def get_all_secured(userRequest):
	allSecured = 0
	collectionList = Collection.objects.filter(request=userRequest.id, status__gte=0)
	for collection in collectionList:
		collection.allSecured = collection.customSecured + collection.taxonSecured
		allSecured += collection.allSecured
	return allSecured

def get_mul_all_secured(request_list):
	collectionList = list(Collection.objects.filter(request__in=[re.id for re in request_list], status__gte=0))
	for r in request_list:
		allSecured = 0
		for collection in [c for c in collectionList if c.request_id == r.id]:
			collection.allSecured = collection.customSecured + collection.taxonSecured
			allSecured += collection.allSecured
		r.allSecured = allSecured
	
def check_all_collections_removed(requestId):
	userRequest = Request.objects.get(id = requestId)
	collectionList = userRequest.collection_set.filter(status__gte=0)
	if not collectionList:
		userRequest.status = -1
		userRequest.changedBy = changed_by("pyha")
		userRequest.save()
		return True
	return False

def create_new_contact(http_request, userRequest, count):
	contact = RequestContact()
	contact.request = userRequest
	contact.personName = http_request.POST.get('request_person_name_'+str(count))
	contact.personStreetAddress = http_request.POST.get('request_person_street_address_'+str(count))
	contact.personPostOfficeName = http_request.POST.get('request_person_post_office_name_'+str(count))
	contact.personPostalCode = http_request.POST.get('request_person_postal_code_'+str(count))
	contact.personCountry = http_request.POST.get('request_person_country_'+str(count))
	contact.personEmail = http_request.POST.get('request_person_email_'+str(count))
	contact.personPhoneNumber = http_request.POST.get('request_person_phone_number_'+str(count))
	contact.personOrganizationName = http_request.POST.get('request_person_organization_name_'+str(count))
	contact.personCorporationId = http_request.POST.get('request_person_corporation_id_'+str(count))
	contact.changedBy = changed_by_session_user(http_request)
	contact.save()

def update_contact_preset(http_request, userRequest):
	contactPreset = ContactPreset.objects.filter(user=userRequest.user).first()
	if contactPreset is None:
		contactPreset = ContactPreset()
	contactPreset.user = userRequest.user
	contactPreset.requestPersonName = http_request.POST.get('request_person_name_1')
	contactPreset.requestPersonStreetAddress = http_request.POST.get('request_person_street_address_1')
	contactPreset.requestPersonPostOfficeName = http_request.POST.get('request_person_post_office_name_1')
	contactPreset.requestPersonPostalCode = http_request.POST.get('request_person_postal_code_1')
	contactPreset.requestPersonCountry = http_request.POST.get('request_person_country_1')
	contactPreset.requestPersonEmail = http_request.POST.get('request_person_email_1')
	contactPreset.requestPersonPhoneNumber = http_request.POST.get('request_person_phone_number_1')
	contactPreset.requestPersonOrganizationName = http_request.POST.get('request_person_organization_name_1')
	contactPreset.requestPersonCorporationId = http_request.POST.get('request_person_corporation_id_1')
	contactPreset.changedBy = changed_by_session_user(http_request)
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
				if wantedRequest.status != StatusEnum.WAITING_FOR_INFORMATION:
					wantedRequest.status = StatusEnum.WAITING
			else:
				wantedRequest.status = StatusEnum.UNKNOWN
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
			if wantedRequest.status != StatusEnum.WAITING_FOR_INFORMATION:
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
		if wantedRequest.status != StatusEnum.WAITING_FOR_INFORMATION:
			wantedRequest.status = StatusEnum.WAITING
	else:
		wantedRequest.status = StatusEnum.UNKNOWN
	if(wantedRequest.status != statusBeforeUpdate):
		wantedRequest.changedBy = changed_by("pyha")
		wantedRequest.save()
	emailsOnUpdate(requestCollections, wantedRequest, lang, statusBeforeUpdate)
		
def handler_mul_req_waiting_for_me_status(request_list, http_request, userId):
	for r in request_list:
		r.waitingstatus = 0
	if CAT_HANDLER_SENS in http_request.session.get("user_roles", [None]):
		for r in request_list:
			if r.sensStatus == 1:
				r.waitingstatus = 1
	if CAT_HANDLER_COLL in http_request.session.get("user_roles", [None]):
		coobList = list(Collection.objects.filter(request__in=[re.id for re in request_list], customSecured__gt = 0, address__in = get_collections_where_download_handler(userId), status = 1))
		for r in request_list:
			if len([x for x in coobList if x.request == r.id]) > 0:
				r.waitingstatus = 1
	return

def handler_req_waiting_for_me_status(r, http_request, userId):
	r.waitingstatus = 0
	if CAT_HANDLER_SENS in http_request.session.get("user_roles", [None]) and r.sensStatus == 1:
		r.waitingstatus = 1
	elif CAT_HANDLER_COLL in http_request.session.get("user_roles", [None]):
		if Collection.objects.filter(request=r.id, customSecured__gt = 0, address__in = get_collections_where_download_handler(userId), status = 1).exists():
			r.waitingstatus = 1
	return


def handler_mul_information_chat_answered_status(request_list, http_request, userId):
	for r in request_list:
		r.answerstatus = 0
	if CAT_HANDLER_SENS in http_request.session.get("user_roles", [None]):
		reqSensChatList = list(RequestInformationChatEntry.requestInformationChat.filter(request__in=[re.id for re in request_list], target='sens'))
		for r in request_list:
			reqsenschat = [x for x in reqSensChatList if x.request_id==r.id]
			if len(reqsenschat) > 0 and r.sensStatus == Sens_StatusEnum.WAITING:
				chat = reqsenschat.sort(key=lambda x:x.date, reverse=True)[0]
				if not chat.question:
					r.answerstatus = 1
	if CAT_HANDLER_COLL in http_request.session.get("user_roles", [None]):
		reqFilteredColChatList = list(RequestInformationChatEntry.requestInformationChat.filter(request__in=[re.id for re in request_list], target__in = get_collections_where_download_handler(userId)))
		coobList = list(Collection.objects.filter(request__in=[re.id for re in request_list], address__in=get_collections_where_download_handler(userId)))
		for r in request_list:
			colist = [co for co in coobList if co.request_id==r.id]
			for co in colist:
				colbasedchatlist = [x for x in reqFilteredColChatList if x.target == co.address and x.request_id==r.id]
				if len(colbasedchatlist) > 0 and co.status == StatusEnum.WAITING:
					latestchat = colbasedchatlist.sort(key=lambda x:x.date, reverse=True)[0]
					if not latestchat.question:
						r.answerstatus = 1
						break
	return

def handler_information_chat_answered_status(r, http_request, userId):
	r.answerstatus = 0
	if CAT_HANDLER_SENS in http_request.session.get("user_roles", [None]):
		if RequestInformationChatEntry.requestInformationChat.filter(request=r.id, target='sens').count() > 0 and r.sensStatus == Sens_StatusEnum.WAITING:
			chat = RequestInformationChatEntry.requestInformationChat.filter(request=r.id, target='sens').order_by('-date')[0]
			if not chat.question:
				r.answerstatus = 1
	if CAT_HANDLER_COLL in http_request.session.get("user_roles", [None]):
		for co in get_collections_where_download_handler(userId):
			if RequestInformationChatEntry.requestInformationChat.filter(request=r.id, target = co).count() > 0 and Collection.objects.get(request=r.id, address=co).status == StatusEnum.WAITING:
				cochat = RequestInformationChatEntry.requestInformationChat.filter(request=r.id, target = co).order_by('-date')[0]
				if not cochat.question:
					r.answerstatus = 1
					break

def create_request_view_context(requestId, http_request, userRequest):
	toast = None
	if(http_request.session.get("toast", None) is not None): 
		toast = http_request.session["toast"]
		http_request.session["toast"] = None
		http_request.session.save()
	taxonList = []
	customList = []
	collectionList = []
	userId = http_request.session["user_id"]
	role1 = CAT_HANDLER_SENS in http_request.session.get("user_roles", [None])
	role2 = CAT_HANDLER_COLL in http_request.session.get("user_roles", [None])
	role3 = CAT_ADMIN in http_request.session.get("user_roles", [None])
	hasServiceRole = role1 or role2 or role3
	lang = http_request.LANGUAGE_CODE
	create_collections_for_lists(requestId, http_request, taxonList, customList, collectionList, userRequest, userId, role1, role2)
	taxon = False
	allSecured = 0
	allQuarantined = 0
	for collection in collectionList:
		collection.allSecured = collection.customSecured + collection.taxonSecured
		allSecured += collection.allSecured
		allQuarantined += collection.quarantineSecured
		if(collection.taxonSecured > 0):
			taxon = True
	request_owner = fetch_user_name(userRequest.user)
	request_owners_email = fetch_email_address(userRequest.user)
	request_log = requestLog(http_request, requestId)
	context = {"toast": toast, "taxonlist": taxonList, "customlist": customList, "taxon": taxon, "role": hasServiceRole, "role1": role1, "role2": role2, "email": http_request.session["user_email"], "userRequest": userRequest, "requestLog_list": request_log, "filters": show_filters(http_request, userRequest), "collections": collectionList, "static": settings.STA_URL, "request_owner": request_owner, "request_owners_email": request_owners_email}
	context["coordinates"] = create_coordinates(userRequest)
	context["filter_link"] = filterlink(userRequest, settings.FILTERS_LINK)
	context["official_filter_link"] = filterlink(userRequest, settings.OFFICIAL_FILTERS_LINK)
	context["tun_link"] = settings.TUN_URL
	context["has_quarantine"] = allQuarantined > 0
	context["sensitivity_terms"] = "pyha/skipofficial/terms/skipofficial_collection-"+lang+".html" if userRequest.sensStatus == Sens_StatusEnum.IGNORE_OFFICIAL else "pyha/official/terms/sensitivity-"+lang+".html"
	context["username"] = http_request.session["user_name"]
	context["allSecured"] = allSecured
	if role2:
		handles = get_collections_where_download_handler(userId)
		context["collections"] = sort_collections_by_download_handler(collectionList, handles)
		context["handles"] = handles
	if role3: 
		emails = {}
		for (lang, name) in settings.LANGUAGES:
			emails[lang] = get_template_of_mail_for_approval(userRequest.id, lang)
		sent_time = get_collection_handlers_autom_email_sent_time()
		if sent_time > get_log_terms_accepted_date_time(request_log): context["com_last_automated_send_email"] = sent_time
		context["com_email_templates"] = emails
		context["com_email_template"] = get_template_of_mail_for_approval(userRequest.id, lang)
	if hasServiceRole: context["handler_groups"] = get_download_handlers_with_collections_listed_for_collections(userRequest.id, collectionList)
	if userRequest.status > StatusEnum.APPROVETERMS_WAIT:
		context["next"] = http_request.GET.get('next', 'history')
		context["contactlist"] = get_request_contacts(userRequest)
		context["reasonlist"] = get_reasons(userRequest)
		if(userRequest.sensStatus == Sens_StatusEnum.IGNORE_OFFICIAL):
			isEndable = (Collection.objects.filter(request=userRequest.id,status=4).exists())
		else:
			isEndable = (Collection.objects.filter(request=userRequest.id, taxonSecured__gt=0, customSecured=0).exists() or Collection.objects.filter(request=userRequest.id,status=4).exists()) and (not taxon or userRequest.sensStatus == Sens_StatusEnum.APPROVED)		
		context["endable"] = isEndable
		context["user"] = userId
		handler_req_waiting_for_me_status(userRequest, http_request, userId)
	if userRequest.status == StatusEnum.DOWNLOADABLE:
		context["download"] = settings.LAJIDOW_URL+userRequest.lajiId+'?personToken='+http_request.session["token"]
		context["downloadable"] = is_downloadable(http_request, userRequest)
	if userRequest.status == StatusEnum.APPROVETERMS_WAIT and Request.objects.filter(user=userId,status__gte=1).count() > 0:
		context["contactPreset"] = ContactPreset.objects.get(user=userId)
	else:
		context["requestSensitiveChat_list"] = requestSensitiveChat(userRequest)
		context["requestHandlerChat_list"] = requestHandlerChat(http_request, userRequest)
		requestInformationChat_list = requestInformationChat(http_request, userRequest, role1, role2, userId)
		context["requestInformationChat_list"] = requestInformationChat_list
		if(requestInformationChat_list):
			context["information"] = not requestInformationChat_list[-1].question
	return context

def is_downloadable(http_request, userRequest):
	if(datetime.strptime(userRequest.downloadDate, "%Y-%m-%d %H:%M:%S.%f") > datetime.now()-timedelta(days=settings.DOWNLOAD_PERIOD_DAYS) and not userRequest.frozen):
		return True
	if(not userRequest.frozen):
		userRequest.frozen = True
		userRequest.changedBy = changed_by_session_user(http_request)
		userRequest.save()
	return False

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

def make_logEntry_view(http_request, userRequest, userId, role1, role2, role3):
	if not "has_viewed" in http_request.session:
		http_request.session["has_viewed"] = []
	if userRequest.id not in http_request.session.get("has_viewed", [None]):
		logRole = USER
		if role3:
			logRole = CAT_ADMIN
		elif role1:
			logRole = CAT_HANDLER_SENS
			if role2:
				logRole = CAT_HANDLER_BOTH 
		elif role2:
			logRole = CAT_HANDLER_COLL
		http_request.session["has_viewed"].append(userRequest.id)
		RequestLogEntry.requestLog.create(request=userRequest, user=userId, role=logRole, action=RequestLogEntry.VIEW)
		

def requestLog(http_request, requestId):
		requestLog_list = list(RequestLogEntry.requestLog.filter(request=requestId).order_by('-date'))
		collectionList = []
		email = []
		for l in requestLog_list:
			if(l.collection):
				collectionList.append(l.collection)
			l.email = fetch_email_address(l.user)
			l.name = fetch_user_name(l.user)
		get_values_for_collections(requestId, http_request, collectionList)
		for l in requestLog_list:
			if(l.collection):
				collectionList.append(l)
		return requestLog_list

def requestSensitiveChat(userRequest):
		requestSensitiveChat_list = list(RequestSensitiveChatEntry.requestChat.filter(request=userRequest).order_by('date'))
		for c in requestSensitiveChat_list:
			c.name = fetch_user_name(c.user)
		return requestSensitiveChat_list
	
def requestHandlerChat(http_request, userRequest):
		requestHandlerChat_list = list(RequestHandlerChatEntry.requestHandlerChat.filter(request=userRequest).order_by('date'))
		for c in requestHandlerChat_list:
			c.name = fetch_user_name(c.user)
			get_result_for_target(http_request, c)
		return requestHandlerChat_list

def requestInformationChat(http_request, userRequest, role1, role2, userId):
		requestInformationChat_list = []
		if HANDLER_ANY in http_request.session.get("current_user_role", [None]):
			if role1:
				requestInformationChat_list += list(RequestInformationChatEntry.requestInformationChat.filter(request=userRequest, target='sens').order_by('date'))
			if role2:
				if userRequest.sensStatus != Sens_StatusEnum.IGNORE_OFFICIAL:
					for collection in Collection.objects.filter(request=userRequest, customSecured__gt = 0, address__in = get_collections_where_download_handler(userId)):
						requestInformationChat_list += list(RequestInformationChatEntry.requestInformationChat.filter(request=userRequest, target=str(collection.address)).order_by('date'))
				else:
					#for collection in Collection.objects.filter(request=userRequest, address__in = get_collections_where_download_handler(userId)):
					for collection in Collection.objects.filter(request=userRequest):
						requestInformationChat_list += list(RequestInformationChatEntry.requestInformationChat.filter(request=userRequest, target=str(collection.address)).order_by('date'))
		else:
			requestInformationChat_list += list(RequestInformationChatEntry.requestInformationChat.filter(request=userRequest).order_by('date'))
		for l in requestInformationChat_list:
			get_result_for_target(http_request, l)
		for l in requestInformationChat_list:
			l.name = fetch_user_name(l.user)
		return requestInformationChat_list
	
def update_sens_status(http_request, userRequest):
	if userRequest.sensStatus != Sens_StatusEnum.IGNORE_OFFICIAL:
		if ADMIN in http_request.session["current_user_role"]:
			collections = Collection.objects.filter(request=userRequest.id, customSecured__lte = 0, taxonSecured__gt=0, status__gte = 0)
			if (int(http_request.POST.get('answer')) == 1):
				userRequest.sensStatus = Sens_StatusEnum.APPROVED
				for co in collections:
					co.status =  Col_StatusEnum.APPROVED
				#make a log entry
				RequestLogEntry.requestLog.create(request = userRequest, user = http_request.session["user_id"], role = CAT_ADMIN, action = RequestLogEntry.DECISION_POSITIVE)
			elif (int(http_request.POST.get('answer')) == 3):                    
				userRequest.sensStatus = Sens_StatusEnum.WAITING
				for co in collections:
					co.status =  Col_StatusEnum.WAITING
				#make a log entry
				RequestLogEntry.requestLog.create(request = userRequest, user = http_request.session["user_id"], role = CAT_ADMIN, action = RequestLogEntry.DECISION_RESET)
			else:
				userRequest.sensStatus = Sens_StatusEnum.REJECTED
				for co in collections:
					co.status =  Col_StatusEnum.REJECTED
				#make a log entry
				RequestLogEntry.requestLog.create(request = userRequest, user = http_request.session["user_id"], role = CAT_ADMIN, action = RequestLogEntry.DECISION_NEGATIVE)
			userRequest.sensDecisionExplanation = http_request.POST.get('reason')
			userRequest.changedBy = changed_by_session_user(http_request)
			userRequest.save()
			update_request_status(userRequest, userRequest.lang)
		elif CAT_HANDLER_SENS in http_request.session["user_roles"]:
			collections = Collection.objects.filter(request=userRequest.id, customSecured__lte = 0, taxonSecured__gt=0, status__gte = 0)
			if (int(http_request.POST.get('answer')) == 1):
				userRequest.sensStatus = Sens_StatusEnum.APPROVED
				for co in collections:
					co.status =  Col_StatusEnum.APPROVED
				#make a log entry
				RequestLogEntry.requestLog.create(request = userRequest, user = http_request.session["user_id"], role = CAT_HANDLER_SENS, action = RequestLogEntry.DECISION_POSITIVE)
			else:
				userRequest.sensStatus = Sens_StatusEnum.REJECTED
				for co in collections:
					co.status =  Col_StatusEnum.REJECTED
				#make a log entry
				RequestLogEntry.requestLog.create(request = userRequest, user = http_request.session["user_id"], role = CAT_HANDLER_SENS, action = RequestLogEntry.DECISION_NEGATIVE)
			userRequest.sensDecisionExplanation = http_request.POST.get('reason')
			userRequest.changedBy = changed_by_session_user(http_request)
			userRequest.save()
			update_request_status(userRequest, userRequest.lang)
	
def update_collection_status(http_request, userRequest, collection):
	if ADMIN in http_request.session["current_user_role"]:
		if (int(http_request.POST.get('answer')) == 1):
			collection.status = Col_StatusEnum.APPROVED
			#make a log entry
			RequestLogEntry.requestLog.create(request = userRequest, collection = collection, user = http_request.session["user_id"], role = CAT_ADMIN, action = RequestLogEntry.DECISION_POSITIVE)
		elif (int(http_request.POST.get('answer')) == 3):                    
			collection.status = Col_StatusEnum.WAITING
			#make a log entry
			RequestLogEntry.requestLog.create(request = userRequest, collection = collection, user = http_request.session["user_id"], role = CAT_ADMIN, action = RequestLogEntry.DECISION_RESET)
		else:
			collection.status = Col_StatusEnum.REJECTED
			#make a log entry
			RequestLogEntry.requestLog.create(request = userRequest,collection = collection, user = http_request.session["user_id"], role = CAT_ADMIN, action = RequestLogEntry.DECISION_NEGATIVE)
		collection.decisionExplanation = http_request.POST.get('reason')
		collection.changedBy = changed_by_session_user(http_request)
		collection.save()
		update_request_status(userRequest, userRequest.lang)
	elif HANDLER_ANY == http_request.session["current_user_role"]:
		if is_download_handler_in_collection(http_request.session["user_id"], collection.address) and userRequest.status != StatusEnum.WAITING_FOR_DOWNLOAD and userRequest.status != StatusEnum.DOWNLOADABLE and userRequest.status != StatusEnum.REJECTED:
			if (int(http_request.POST.get('answer')) == 1):
				collection.status = Col_StatusEnum.APPROVED
				#make a log entry
				RequestLogEntry.requestLog.create(request = userRequest, collection = collection, user = http_request.session["user_id"], role = CAT_HANDLER_COLL, action = RequestLogEntry.DECISION_POSITIVE)
			else:
				collection.status = Col_StatusEnum.REJECTED
				#make a log entry
				RequestLogEntry.requestLog.create(request = userRequest, collection = collection, user = http_request.session["user_id"], role = CAT_HANDLER_COLL, action = RequestLogEntry.DECISION_NEGATIVE)
			collection.decisionExplanation = http_request.POST.get('reason')
			collection.changedBy = changed_by_session_user(http_request)
			collection.save()
			update_request_status(userRequest, userRequest.lang)
	
def get_collections_waiting_atleast_days(days_to_subtract):
	return Collection.objects.filter(request__in=Request.objects.filter(id__in=RequestLogEntry.requestLog.filter(action=RequestLogEntry.ACCEPT, date__lt = datetime.today() - timedelta(days=days_to_subtract)).values("request"), status=StatusEnum.WAITING, frozen=False), status = Col_StatusEnum.WAITING)

def is_collection_waiting_atleast_days(days_to_subtract, collection):
	return Request.objects.filter(id=collection.request.id, status=StatusEnum.WAITING, frozen=False).count() > 0 and Collection.objects.filter(id = collection.id, status = Col_StatusEnum.WAITING).count() > 0 and RequestLogEntry.requestLog.filter(request=collection.request, action=RequestLogEntry.ACCEPT, date__lt = datetime.today() - timedelta(days=days_to_subtract)).count() > 0

def contains_approved_collection(requestId):
	return Collection.objects.filter(request=requestId, status = Col_StatusEnum.APPROVED).count() > 0

def sort_collections_by_download_handler(collectionList, handles):
    not_handle = []
    handle = []
    for collection in collectionList:
        if collection.address in handles:
            handle.append(collection)
        else:
            not_handle.append(collection)
    handle.extend(not_handle)
    return handle

def get_log_terms_accepted_date_time(request_log):
	for log_entry in request_log:
		if log_entry.action == RequestLogEntry().ACCEPT:
			return log_entry.date
	return None

def update_collection_handlers_autom_email_sent_time():    
	caches['collections'].set('last_timed_email', datetime.now())
	return True

def get_collection_handlers_autom_email_sent_time():    
	return caches['collections'].get('last_timed_email', None)

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
		if c.status != Col_StatusEnum.WAITING:
			collectionsNotHandled -=1
	#check if request is handled
	if collectionsNotHandled == 0 and (userRequest.sensStatus == Sens_StatusEnum.REJECTED or userRequest.sensStatus == Sens_StatusEnum.APPROVED or userRequest.sensStatus == Sens_StatusEnum.APPROVETERMS_WAIT or userRequest.sensStatus == Sens_StatusEnum.IGNORE_OFFICIAL):
		send_mail_after_request_has_been_handled_to_requester(userRequest.id, lang)
	elif(statusBeforeUpdate!=userRequest.status):
		#Send email if status changed
		send_mail_after_request_status_change_to_requester(userRequest.id, lang)








