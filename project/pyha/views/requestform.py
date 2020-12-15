import json

from django.utils.translation import ugettext
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from pyha.database import create_request_view_context, check_all_collections_removed, create_new_contact, update_contact_preset
from pyha.email import send_mail_after_approving_terms, send_admin_mail_after_approved_request, send_admin_mail_after_approved_request_missing_handlers
from pyha.localization import check_language
from pyha.login import logged_in, _process_auth_response, is_allowed_to_view
from pyha.models import RequestLogEntry, Request, Collection, StatusEnum, Col_StatusEnum, AdminUserSettings
from pyha.warehouse import is_collections_missing_download_handler, fetch_email_address
from pyha.roles import USER
from pyha.log_utils import changed_by_session_user
from pyha import toast


def removeCollection(http_request):
    if http_request.method == 'POST':
        if not logged_in(http_request):
            return _process_auth_response(http_request, "pyha")
        requestId = http_request.POST.get('requestid', '?')
        if not is_allowed_to_view(http_request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        collectionId = http_request.POST.get('collectionid')
        redirect_path = http_request.POST.get('next')
        collection = Collection.objects.get(address = collectionId, request = requestId)
        if not is_allowed_to_view(http_request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        #avoid work when submitted multiple times
        if(collection.status != -1):
            collection.status = -1
            collection.save()
            collection.changedBy = changed_by_session_user(http_request)
            check_all_collections_removed(requestId)
        return HttpResponseRedirect(redirect_path)
    return HttpResponseRedirect(reverse('pyha:root'))


def approve_terms(http_request):
    if http_request.method == 'POST':
        if not logged_in(http_request):
            return _process_auth_response(http_request, "pyha")
        requestId = http_request.POST.get('requestid', '?')
        if not is_allowed_to_view(http_request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        lang = 'fi' #ainakin toistaiseksi
        userRequest = Request.objects.get(id = requestId)
        approve_terms_skip_official(http_request, userRequest, requestId, lang)
    return HttpResponseRedirect(reverse('pyha:root'))


def approve_terms_skip_official(http_request, userRequest, requestId, lang):
    senschecked = http_request.POST.get('checkbsens')
    collectionList = Collection.objects.filter(request=requestId, status__gte=0)
    if(userRequest.status == 0 and senschecked and len(collectionList) > 0):
        for c in collectionList:
            if c.status == 0:
                c.status = 1
                c.changedBy = changed_by_session_user(http_request)
                c.save()

        for count in range(2, count_contacts(http_request.POST)+1):
            create_new_contact(http_request, userRequest, count)

        userRequest.reason = create_argument_blob(http_request)
        userRequest.status = 1
        userRequest.personName = http_request.POST.get('request_person_name_1')
        userRequest.personStreetAddress = http_request.POST.get('request_person_street_address_1')
        userRequest.personPostOfficeName = http_request.POST.get('request_person_post_office_name_1')
        userRequest.personPostalCode = http_request.POST.get('request_person_postal_code_1')
        userRequest.personCountry = http_request.POST.get('request_person_country_1')
        userRequest.personEmail = http_request.POST.get('request_person_email_1')
        userRequest.personPhoneNumber = http_request.POST.get('request_person_phone_number_1')
        userRequest.personOrganizationName = http_request.POST.get('request_person_organization_name_1')
        userRequest.personCorporationId = http_request.POST.get('request_person_corporation_id_1')
        userRequest.changedBy = changed_by_session_user(http_request)
        userRequest.save()
        update_contact_preset(http_request, userRequest)
        #make a log entry
        RequestLogEntry.requestLog.create(request=userRequest, user=http_request.session["user_id"], role=USER, action=RequestLogEntry.ACCEPT)
        http_request.session["toast"] = {"status": toast.POSITIVE , "message": ugettext('toast_thanks_request_has_been_registered')}
        http_request.session.save()

        missing_handlers = is_collections_missing_download_handler(collectionList)
        for setting in AdminUserSettings.objects.all():
            email = fetch_email_address(setting.user)
            if(setting.enableCustomEmailAddress): email = setting.customEmailAddress
            if(setting.emailNewRequests == AdminUserSettings.ALL):
                if missing_handlers:
                    send_admin_mail_after_approved_request_missing_handlers(requestId, email)
                else:
                    send_admin_mail_after_approved_request(requestId, email)
            elif(setting.emailNewRequests == AdminUserSettings.MISSING and missing_handlers):
                send_admin_mail_after_approved_request_missing_handlers(requestId, email)

        send_mail_after_approving_terms(requestId, userRequest.lang)
    else:
        userRequest.status = -1
        userRequest.changedBy = changed_by_session_user(http_request)
        userRequest.save()
        RequestLogEntry.requestLog.create(request=userRequest, user=http_request.session["user_id"], role=USER, action=RequestLogEntry.ACCEPT)

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

def count_contacts(post):
    i = 0
    for string in post:
        if "request_person_name" in string:
            i += 1
    return i
