import json

from django.utils.translation import ugettext
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from pyha.database import create_request_view_context, check_all_collections_removed, create_new_contact, update_contact_preset
from pyha.email import send_mail_for_approval, send_mail_for_approval_sens
from pyha.localization import check_language
from pyha.login import logged_in, _process_auth_response, is_allowed_to_view
from pyha.models import RequestLogEntry, Request, Collection, StatusEnum, Sens_StatusEnum, Col_StatusEnum
from pyha.roles import USER
from pyha.log_utils import changed_by_session_user
from pyha import toast


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
        next = request.POST.get('next', '/')
        collectionId = request.POST.get('collectionId')
        requestId = request.POST.get('requestid')
        collection = Collection.objects.get(id = collectionId)
        collection.customSecured = 0
        collection.changedBy = changed_by_session_user(request)
        collection.save()
        if(collection.taxonSecured == 0) and (collection.status != -1):
            collection.status = -1
            collection.changedBy = changed_by_session_user(request)
            collection.save()
            check_all_collections_removed(requestId)
        return HttpResponseRedirect(next)
    return HttpResponseRedirect(reverse('pyha:root'))

def removeCollection(request):
    if request.method == 'POST':
        if not logged_in(request):
            return _process_auth_response(request, "pyha")
        requestId = request.POST.get('requestid', '?')
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        collectionId = request.POST.get('collectionid')
        redirect_path = request.POST.get('next')
        collection = Collection.objects.get(address = collectionId, request = requestId)
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        #avoid work when submitted multiple times
        if(collection.status != -1):
            collection.status = -1
            collection.save()
            collection.changedBy = changed_by_session_user(request)
            check_all_collections_removed(requestId)
        return HttpResponseRedirect(redirect_path)
    return HttpResponseRedirect(reverse('pyha:root'))


def approve_terms(request):
    if request.method == 'POST':
        if not logged_in(request):
            return _process_auth_response(request, "pyha")
        requestId = request.POST.get('requestid', '?')
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        lang = 'fi' #ainakin toistaiseksi
        userRequest = Request.objects.get(id = requestId)
        if userRequest.sensStatus == Sens_StatusEnum.IGNORE_OFFICIAL:
            approve_terms_skip_official(request, userRequest, requestId, lang)
        else:
            requestedCollections = request.POST.getlist('checkb')
            senschecked = request.POST.get('checkbsens')
            collectionList = Collection.objects.filter(request=requestId, status__gte=0)
            if(userRequest.status == StatusEnum.APPROVETERMS_WAIT and senschecked and len(collectionList) > 0):
                taxon = False
                for collection in collectionList:
                    collection.allSecured = collection.customSecured + collection.taxonSecured
                    if(collection.taxonSecured > 0):
                        taxon = True
                if len(requestedCollections) > 0:
                    for rc in requestedCollections:
                        userCollection = Collection.objects.get(address = rc, request = requestId)
                        if userCollection.status == 0:
                            userCollection.status = 1
                            userCollection.changedBy = changed_by_session_user(request)
                            userCollection.save()
                for c in Collection.objects.filter(request = requestId):
                    if c.status == 0:
                        c.customSecured = 0
                        if userRequest.sensStatus == Sens_StatusEnum.APPROVETERMS_WAIT:
                            c.taxonsecured = 0
                        c.changedBy = changed_by_session_user(request)
                        c.save()
                        if c.taxonSecured == 0:
                            c.status = -1
                            c.changedBy = changed_by_session_user(request)
                            c.save()
                    #postia vain niille aineistoille, joilla on aineistokohtaisesti salattuja tietoja
                    #if(c.customSecured > 0):
                    #    send_mail_for_approval(requestId, c, lang)
    
                for count in range(2, count_contacts(request.POST)+1):
                    create_new_contact(request, userRequest, count)
    
                userRequest.reason = create_argument_blob(request)
                userRequest.status = 1
                if senschecked:
                    if not taxon:
                        userRequest.sensStatus = 4
                    else:
                        userRequest.sensStatus = 1
                userRequest.personName = request.POST.get('request_person_name_1')
                userRequest.personStreetAddress = request.POST.get('request_person_street_address_1')
                userRequest.personPostOfficeName = request.POST.get('request_person_post_office_name_1')
                userRequest.personPostalCode = request.POST.get('request_person_postal_code_1')
                userRequest.personCountry = request.POST.get('request_person_country_1')
                userRequest.personEmail = request.POST.get('request_person_email_1')
                userRequest.personPhoneNumber = request.POST.get('request_person_phone_number_1')
                userRequest.personOrganizationName = request.POST.get('request_person_organization_name_1')
                userRequest.personCorporationId = request.POST.get('request_person_corporation_id_1')
                userRequest.changedBy = changed_by_session_user(request)
                userRequest.save()
                update_contact_preset(request, userRequest)
                #if userRequest.sensstatus == 1 and taxon:
                    #send_mail_for_approval_sens(requestId, lang)
                #make a log entry
                RequestLogEntry.requestLog.create(request=userRequest, user=request.session["user_id"], role=USER, action=RequestLogEntry.ACCEPT)
                request.session["toast"] = {"status": toast.POSITIVE , "message": ugettext('toast_thanks_request_has_been_registered')}
                request.session.save()
            else:
                userRequest.status = -1
                userRequest.changedBy = changed_by_session_user(request)
                userRequest.save()
                RequestLogEntry.requestLog.create(request=userRequest, user=request.session["user_id"], role=USER, action=RequestLogEntry.ACCEPT)
    return HttpResponseRedirect(reverse('pyha:root'))


def approve_terms_skip_official(request, userRequest, requestId, lang):
    senschecked = request.POST.get('checkbsens')
    collectionList = Collection.objects.filter(request=requestId, status__gte=0)
    if(userRequest.status == 0 and senschecked and len(collectionList) > 0):
        for c in collectionList:
            if c.status == 0:
                c.status = 1
                c.changedBy = changed_by_session_user(request)
                c.save()

        for count in range(2, count_contacts(request.POST)+1):
            create_new_contact(request, userRequest, count)

        userRequest.reason = create_argument_blob(request)
        userRequest.status = 1
        userRequest.personName = request.POST.get('request_person_name_1')
        userRequest.personStreetAddress = request.POST.get('request_person_street_address_1')
        userRequest.personPostOfficeName = request.POST.get('request_person_post_office_name_1')
        userRequest.personPostalCode = request.POST.get('request_person_postal_code_1')
        userRequest.personCountry = request.POST.get('request_person_country_1')
        userRequest.personEmail = request.POST.get('request_person_email_1')
        userRequest.personPhoneNumber = request.POST.get('request_person_phone_number_1')
        userRequest.personOrganizationName = request.POST.get('request_person_organization_name_1')
        userRequest.personCorporationId = request.POST.get('request_person_corporation_id_1')
        userRequest.changedBy = changed_by_session_user(request)
        userRequest.save()
        update_contact_preset(request, userRequest)
        #make a log entry
        RequestLogEntry.requestLog.create(request=userRequest, user=request.session["user_id"], role=USER, action=RequestLogEntry.ACCEPT)
        request.session["toast"] = {"status": toast.POSITIVE , "message": ugettext('toast_thanks_request_has_been_registered')}
        request.session.save()
    else:
        userRequest.status = -1
        userRequest.changedBy = changed_by_session_user(request)
        userRequest.save()
        RequestLogEntry.requestLog.create(request=userRequest, user=request.session["user_id"], role=USER, action=RequestLogEntry.ACCEPT)
    return

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
