import json
from argparse import Namespace
from datetime import timedelta, datetime
from django.core.cache import caches
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseRedirect
from django.db.models import Count, Sum, Case, When, IntegerField, Q, F, Subquery, OuterRef
from pyha.email import send_mail_after_request_has_been_handled_to_requester, send_mail_after_request_status_change_to_requester, get_template_of_mail_for_approval
from pyha.login import logged_in, _process_auth_response, is_request_owner
from pyha.models import RequestLogEntry, RequestHandlerChatEntry, RequestInformationChatEntry, ContactPreset, RequestContact, Collection, Request, StatusEnum,\
    Col_StatusEnum, RequestSentStatusEmail, FailedDownloadRequest
from pyha.roles import HANDLER_ANY, CAT_HANDLER_COLL, USER, ADMIN, CAT_ADMIN
from pyha.warehouse import get_values_for_collections, send_download_request, fetch_user_name, fetch_email_address, show_filters, get_result_for_target, get_collections_where_download_handler, update_collections, get_download_handlers_with_collections_listed_for_collections, is_download_handler_in_collection, get_collection_counts, get_collection_count_sum, get_filter_link
from pyha.log_utils import changed_by_session_user, changed_by


def removeCollection(http_request):
    if http_request.method == 'POST':
        if not logged_in(http_request):
            return _process_auth_response(http_request, "pyha")
        requestId = http_request.POST.get('requestid', '?')
        if not is_request_owner(http_request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        nextRedirect = http_request.POST.get('next', '/')
        collectionId = http_request.POST.get('collectionid')
        collection = Collection.objects.get(address=collectionId, request=requestId)
        if(collection.status != -1):
            collection.status = -1
            collection.changedBy = changed_by_session_user(http_request)
            collection.save()
            check_all_collections_removed(requestId)
        return HttpResponseRedirect(nextRedirect)
    return HttpResponseRedirect(reverse('pyha:root'))


def remove_request(request, http_request):
    collections = Collection.objects.filter(request=request.id)
    for collection in collections:
        if collection.status != StatusEnum.DISCARDED:
            collection.status = StatusEnum.DISCARDED
            collection.changedBy = changed_by('pyha')
            collection.save()
    if request.status != StatusEnum.DISCARDED:
        request.status = StatusEnum.DISCARDED
        request.changedBy = changed_by_session_user(http_request)
        request.save()


def withdraw_request(request, http_request):
    if request.status != StatusEnum.WITHDRAWN:
        request.status = StatusEnum.WITHDRAWN
        request.frozen = True
        request.changedBy = changed_by_session_user(http_request)
        request.save()


def get_collection_list(userRequest, lang):
    collection_list = Collection.objects.filter(request=userRequest.id, status__gte=0)
    get_values_for_collections(userRequest.id, lang, collection_list)
    for collection in collection_list:
        collection.counts = get_collection_counts(collection, lang)
    return collection_list


def check_all_collections_removed(requestId):
    userRequest = Request.objects.get(id=requestId)
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
    if target == 'admin':
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
    return len(get_unhandled_requests_data(userId))


def get_unhandled_requests_data(userId):
    unhandled = []

    user_collections = get_collections_where_download_handler(userId)
    collection_list = Collection.objects.filter(address__in=user_collections, status=StatusEnum.WAITING)
    request_list = Request.objects.filter(status=StatusEnum.WAITING, frozen=False).filter(
        id__in=collection_list.values("request"))

    for r in request_list:
        request_collections = collection_list.filter(request=r.id).values_list("address", flat=True)

        questioning = False
        for co in request_collections:
            if RequestInformationChatEntry.requestInformationChat.filter(request=r.id, target=co).count() > 0:
                cochat = RequestInformationChatEntry.requestInformationChat.filter(
                    request=r.id, target=co).order_by('-date')[0]
                if cochat.question:
                    questioning = True
                    break

        if not questioning:
            unhandled.append({
                'request_id': r.id,
                'collections': request_collections
            })
    return unhandled


def update_request_status(userRequest, lang):
    if(not userRequest.status in [StatusEnum.WITHDRAWN, StatusEnum.WAITING_FOR_DOWNLOAD, StatusEnum.DOWNLOADABLE]):
        ignore_official_database_update_request_status(userRequest, lang)


def ignore_official_database_update_request_status(wantedRequest, lang):
    statusBeforeUpdate = wantedRequest.status
    accepted, declined, pending = get_collection_status_counts(wantedRequest.id)

    if pending > 0:
        if wantedRequest.status != StatusEnum.WAITING_FOR_INFORMATION:
            wantedRequest.status = StatusEnum.WAITING
    elif accepted > 0:
        try_to_send_download_request(wantedRequest)
        wantedRequest.status = StatusEnum.WAITING_FOR_DOWNLOAD
    elif declined > 0:
        wantedRequest.status = StatusEnum.REJECTED
    else:
        wantedRequest.status = StatusEnum.UNKNOWN

    if(wantedRequest.status != statusBeforeUpdate):
        wantedRequest.changedBy = changed_by("pyha")
        wantedRequest.save()
        emailsOnUpdate(pending, wantedRequest, lang)


def try_to_send_download_request(user_request):
    success = send_download_request(user_request.id)
    if not success:
        create_new_failed_download_request(user_request)


def get_collection_status_counts(request_id):
    collections = Collection.objects.filter(request=request_id, status__gte=0)

    accepted = 0
    declined = 0
    pending = 0

    for c in collections:
        if c.status == StatusEnum.WAITING:
            pending += 1
        elif c.status == StatusEnum.REJECTED:
            declined += 1
        elif c.status == StatusEnum.APPROVED:
            accepted += 1

    return accepted, declined, pending


def get_all_waiting_requests():
    return Request.objects.filter(status=StatusEnum.WAITING)


def handler_req_waiting_for_me_status(r, http_request, userId):
    r.waitingstatus = 0
    if CAT_HANDLER_COLL in http_request.session.get("user_roles", [None]):
        if Collection.objects.filter(request=r.id, address__in=get_collections_where_download_handler(userId), status=1).exists():
            r.waitingstatus = 1
    return


def handler_information_chat_answered_status(r, http_request, userId):
    r.answerstatus = 0
    if CAT_HANDLER_COLL in http_request.session.get("user_roles", [None]):
        for co in get_collections_where_download_handler(userId):
            if RequestInformationChatEntry.requestInformationChat.filter(request=r.id, target=co).count() > 0 and Collection.objects.get(request=r.id, address=co).status == StatusEnum.WAITING:
                cochat = RequestInformationChatEntry.requestInformationChat.filter(
                    request=r.id, target=co).order_by('-date')[0]
                if not cochat.question:
                    r.answerstatus = 1
                    break


def create_request_view_context(requestId, http_request, userRequest):
    toast = None
    if(http_request.session.get("toast", None) is not None):
        toast = http_request.session["toast"]
        http_request.session["toast"] = None
        http_request.session.save()

    userId = http_request.session["user_id"]
    role = http_request.session.get("current_user_role", USER)
    hasServiceRole = (role == HANDLER_ANY or role == ADMIN)
    lang = http_request.LANGUAGE_CODE

    collectionList = get_collection_list(userRequest, http_request.LANGUAGE_CODE)

    request_owner = fetch_user_name(userRequest.user)
    request_owners_email = fetch_email_address(userRequest.user)
    request_log = requestLog(http_request, requestId)
    context = {
        "toast": toast,
        "email": http_request.session["user_email"],
        "userRequest": userRequest,
        "gisDownloadDisabled": userRequest.approximateMatches > settings.GIS_DOWNLOAD_LIMIT,
        "filters": show_filters(userRequest, http_request.LANGUAGE_CODE),
        "collections": collectionList,
        "static": settings.STA_URL,
        "version": settings.VERSION,
        "request_owner": request_owner,
        "request_owners_email": request_owners_email,
        "requestLog_list": request_log if (role == HANDLER_ANY or role == ADMIN) else list(
            filter(lambda x: x.action != RequestLogEntry.VIEW, request_log)
        ),
        "filter_link": get_filter_link(http_request, userRequest, role),
        "tun_link": settings.TUN_URL,
        "sensitivity_terms": "pyha/requestform/terms/collection-" + lang + ".html",
        "username": http_request.session["user_name"],
        "role": role,
        "download_types": Namespace(standard=Request.STANDARD, api_key=Request.API_KEY),
        "api_key_expires_options": Namespace(three_months=Request.THREE_MONTHS, year=Request.YEAR)
    }
    if role == HANDLER_ANY:
        handles = get_collections_where_download_handler(userId)
        context["collections"], context["own_collection_count"] = sort_collections_by_download_handler(
            collectionList, handles)
        context["handles"] = handles
    if role == ADMIN:
        sent_time = get_collection_handlers_autom_email_sent_time()
        accepted_time = get_log_terms_accepted_date_time(request_log)
        if accepted_time != None and sent_time > accepted_time:
            context["com_last_automated_send_email"] = sent_time
        context["com_email_template"] = get_template_of_mail_for_approval(userRequest.id, 'fi')
        context["own_collection_count"] = len(collectionList)
    if hasServiceRole:
        context["handler_groups"] = get_download_handlers_with_collections_listed_for_collections(
            userRequest.id, collectionList)
    if userRequest.status != StatusEnum.APPROVETERMS_WAIT:
        context["next"] = http_request.GET.get('next', 'history')
        context["contactlist"] = get_request_contacts(userRequest)
        context["reasonlist"] = get_reasons(userRequest)
        isEndable = (Collection.objects.filter(request=userRequest.id, status=4).exists())
        context["endable"] = isEndable
        context["user"] = userId
        handler_req_waiting_for_me_status(userRequest, http_request, userId)
    if userRequest.status == StatusEnum.DOWNLOADABLE:
        context["downloadable"] = is_downloadable(http_request, userRequest)
    if userRequest.status == StatusEnum.APPROVETERMS_WAIT and Request.objects.filter(user=userId, status__gte=1).count() > 0:
        context["contactPreset"] = ContactPreset.objects.get(user=userId)
    else:
        context["requestHandlerChat_list"] = requestHandlerChat(http_request, userRequest)
        requestInformationChat_list = requestInformationChat(http_request, userRequest, userId)
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
            t = (f, getattr(fields, f))
            tuplist.append(t)
        reasonlist.fields = tuplist
        return reasonlist
    return None


def make_logEntry_view(http_request, userRequest, userId, role):
    if not "has_viewed" in http_request.session:
        http_request.session["has_viewed"] = []
    if userRequest.id not in http_request.session.get("has_viewed", [None]):
        logRole = USER
        if role == ADMIN:
            logRole = CAT_ADMIN
        elif role == HANDLER_ANY:
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
    get_values_for_collections(requestId, http_request.LANGUAGE_CODE, collectionList)
    for l in requestLog_list:
        if(l.collection):
            collectionList.append(l)
    return requestLog_list


def requestHandlerChat(http_request, userRequest):
    requestHandlerChat_list = list(RequestHandlerChatEntry.requestHandlerChat.filter(
        request=userRequest).order_by('date'))
    for c in requestHandlerChat_list:
        c.name = fetch_user_name(c.user)
        get_result_for_target(http_request, c)
    return requestHandlerChat_list


def requestInformationChat(http_request, userRequest, userId):
    requestInformationChat_list = list(
        RequestInformationChatEntry.requestInformationChat.filter(request=userRequest).order_by('date'))
    for l in requestInformationChat_list:
        get_result_for_target(http_request, l)
    for l in requestInformationChat_list:
        l.name = fetch_user_name(l.user)
    return requestInformationChat_list


def add_last_chat_entry_status_to_request_list(request_list):
    return request_list.annotate(
        last_chat_entry_is_question=Subquery(
            RequestInformationChatEntry.requestInformationChat.filter(
                request=OuterRef('pk')
            ).order_by('-date').values('question')[:1]
        )
    )


def add_collection_counts_to_request_list(request_list, user_collections=None):
    request_list = request_list.annotate(
        waiting_count=Count(Case(
            When(collections__status=Col_StatusEnum.WAITING, then=1),
            output_field=IntegerField()
        )),
        handled_count=Count(Case(
            When(
                Q(collections__status=Col_StatusEnum.APPROVED) | Q(collections__status=Col_StatusEnum.REJECTED),
                then=1
            ),
            output_field=IntegerField()
        )),
        observation_count=Sum(Case(
            When(~Q(collections__status=Col_StatusEnum.DISCARDED), then=F('collections__count_sum')),
            output_field=IntegerField()
        ))
    )

    if user_collections is not None:
        request_list = request_list.annotate(
            waiting_for_user_count=Count(Case(
                When(
                    Q(collections__status=Col_StatusEnum.WAITING) & Q(collections__address__in=user_collections),
                    then=1
                ),
                output_field=IntegerField()
            ))
        )

    return request_list


def update_collection_status(http_request, userRequest, collection):
    if ADMIN in http_request.session["current_user_role"]:
        if (int(http_request.POST.get('answer')) == 1):
            collection.status = Col_StatusEnum.APPROVED
            # make a log entry
            RequestLogEntry.requestLog.create(request=userRequest, collection=collection,
                                              user=http_request.session["user_id"], role=CAT_ADMIN, action=RequestLogEntry.DECISION_POSITIVE)
        elif (int(http_request.POST.get('answer')) == 3):
            collection.status = Col_StatusEnum.WAITING
            # make a log entry
            RequestLogEntry.requestLog.create(request=userRequest, collection=collection,
                                              user=http_request.session["user_id"], role=CAT_ADMIN, action=RequestLogEntry.DECISION_RESET)
        else:
            collection.status = Col_StatusEnum.REJECTED
            # make a log entry
            RequestLogEntry.requestLog.create(request=userRequest, collection=collection,
                                              user=http_request.session["user_id"], role=CAT_ADMIN, action=RequestLogEntry.DECISION_NEGATIVE)
        collection.decisionExplanation = http_request.POST.get('reason')
        collection.changedBy = changed_by_session_user(http_request)
        collection.save()
        update_request_status(userRequest, userRequest.lang)
    elif HANDLER_ANY == http_request.session["current_user_role"]:
        if is_download_handler_in_collection(http_request.session["user_id"], collection.address) and userRequest.status != StatusEnum.WAITING_FOR_DOWNLOAD and userRequest.status != StatusEnum.DOWNLOADABLE and userRequest.status != StatusEnum.REJECTED:
            if (int(http_request.POST.get('answer')) == 1):
                collection.status = Col_StatusEnum.APPROVED
                # make a log entry
                RequestLogEntry.requestLog.create(request=userRequest, collection=collection,
                                                  user=http_request.session["user_id"], role=CAT_HANDLER_COLL, action=RequestLogEntry.DECISION_POSITIVE)
            else:
                collection.status = Col_StatusEnum.REJECTED
                # make a log entry
                RequestLogEntry.requestLog.create(request=userRequest, collection=collection,
                                                  user=http_request.session["user_id"], role=CAT_HANDLER_COLL, action=RequestLogEntry.DECISION_NEGATIVE)
            collection.decisionExplanation = http_request.POST.get('reason')
            collection.changedBy = changed_by_session_user(http_request)
            collection.save()
            update_request_status(userRequest, userRequest.lang)


def accept_empty_collections_automatically(userRequest, collectionList):
    accepted = []

    for collection in collectionList:
        obs_count = get_collection_count_sum(collection)
        if obs_count == 0:
            collection.status = Col_StatusEnum.APPROVED
            collection.changedBy = changed_by("pyha")
            collection.save()
            RequestLogEntry.requestLog.create(request=Request.objects.get(
                id=collection.request.id), collection=collection, user="Laji.fi ICT-team", role=CAT_HANDLER_COLL, action=RequestLogEntry.DECISION_POSITIVE)
            update_request_status(userRequest, userRequest.lang)
            accepted.append(collection)

    return accepted


def get_collections_waiting_atleast_days(days_to_subtract):
    return Collection.objects.filter(request__in=Request.objects.filter(id__in=RequestLogEntry.requestLog.filter(action=RequestLogEntry.ACCEPT, date__lt=datetime.today() - timedelta(days=days_to_subtract)).values("request"), status=StatusEnum.WAITING, frozen=False), status=Col_StatusEnum.WAITING)


def is_collection_waiting_atleast_days(days_to_subtract, collection):
    return Request.objects.filter(id=collection.request.id, status=StatusEnum.WAITING, frozen=False).count() > 0 and Collection.objects.filter(id=collection.id, status=Col_StatusEnum.WAITING).count() > 0 and RequestLogEntry.requestLog.filter(request=collection.request, action=RequestLogEntry.ACCEPT, date__lt=datetime.today() - timedelta(days=days_to_subtract)).count() > 0


def contains_approved_collection(requestId):
    return Collection.objects.filter(request=requestId, status=Col_StatusEnum.APPROVED).count() > 0


def sort_collections_by_download_handler(collectionList, handles):
    not_handle = []
    handle = []
    for collection in collectionList:
        if collection.address in handles:
            handle.append(collection)
        else:
            not_handle.append(collection)
    handle_count = len(handle)
    handle.extend(not_handle)
    return handle, handle_count


def get_log_terms_accepted_date_time(request_log):
    for log_entry in request_log:
        if log_entry.action == RequestLogEntry().ACCEPT:
            return log_entry.date
    return None


def update_collection_handlers_autom_email_sent_time():
    caches['collections'].set('last_timed_email', datetime.now())
    return True


def get_collection_handlers_autom_email_sent_time():
    return caches['collections'].get('last_timed_email', datetime(1999, 1, 1))


"""
    Send "request has been handled" email
    IF request's collections have status != 1(waiting for approval)
"""


def emailsOnUpdate(pending, userRequest, lang):
    if pending == 0:
        send_mail_after_request_has_been_handled_to_requester(userRequest.id, lang)
    else:
        # Send email if status changed
        send_mail_after_request_status_change_to_requester(userRequest.id, lang)


def get_latest_request_sent_status_email(requestId):
    return RequestSentStatusEmail.objects.filter(request=requestId).order_by('date').last()


def save_request_sent_status_email(request, accepted, declined, pending):
    RequestSentStatusEmail.objects.create(request=request, accepted_count=accepted,
                                          declined_count=declined, pending_count=pending)


def create_new_failed_download_request(user_request):
    failed_request = FailedDownloadRequest()
    failed_request.request = user_request
    failed_request.save()


def get_failed_download_requests():
    return FailedDownloadRequest.objects.all().order_by('date')
