from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from pyha.login import logged_in, _process_auth_response, is_allowed_to_view
from pyha.warehouse import store
from pyha.database import create_request_view_context, check_all_collections_removed, create_new_contact, update_contact_preset
from pyha.models import RequestLogEntry
from pyha.roles import *
from pyha.email import *
from pyha.localization import *


def get_taxon(request):
    if request.method == 'POST' and request.POST.get('requestid'):
        if check_language(request):
                return HttpResponseRedirect(request.get_full_path())
        #Has Access
        requestId = request.POST.get('requestid')
        if not logged_in(request):
            return HttpResponse("/pyha/", status=310)
        userRequest = Request.requests.get(id=requestId)
        if not is_allowed_to_view(request, requestId):
            return HttpResponse("/pyha/", status=310)
        context = create_request_view_context(requestId, request, userRequest)
        return render(request, 'pyha/requestformtaxon.html', context)
    return HttpResponse("/pyha/", status=310)
    
def get_custom(request):
    if request.method == 'POST' and request.POST.get('requestid'):
        if check_language(request):
                return HttpResponseRedirect(request.get_full_path())
        #Has Access
        requestId = request.POST.get('requestid')
        if not logged_in(request):
            return HttpResponse("/pyha/", status=310)
        userRequest = Request.requests.get(id=requestId)        
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect('/pyha/')
        context = create_request_view_context(requestId, request, userRequest)
        return render(request, 'pyha/requestformcustom.html', context)
    return HttpResponse("/pyha/", status=310)
    
def get_summary(request):
    if request.method == 'POST' and request.POST.get('requestid'):
        if check_language(request):
                return HttpResponseRedirect(request.get_full_path())
        #Has Access
        requestId = request.POST.get('requestid')
        if not logged_in(request):
            return HttpResponse("/pyha/", status=310)
        userRequest = Request.requests.get(id=requestId)
        if not is_allowed_to_view(request, requestId):
            return HttpResponse("/pyha/", status=310)
        context = create_request_view_context(requestId, request, userRequest)
        return render(request, 'pyha/requestformsummary.html', context)
    return HttpResponse("/pyha/", status=310)

def create_contact_ajax(request):
    if request.method == 'POST' and request.POST.get('requestid') and request.POST.get('id'):
        if check_language(request):
                return HttpResponseRedirect(request.get_full_path())
        #Has Access
        requestId = request.POST.get('requestid','?')
        if not logged_in(request):
            return _process_auth_response(request, "request/"+requestId)
        userRequest = Request.requests.get(id=requestId)   
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect('/pyha/')
        context = create_request_view_context(requestId, request, userRequest)
        context["contact_id"] = request.POST.get('id')
        return render(request, 'pyha/requestformcontact.xml', context)
    return HttpResponse("/pyha/")

def remove_ajax(request):
    if request.method == 'POST' and request.POST.get('requestid'):
        if check_language(request):
                return HttpResponseRedirect(request.get_full_path())
        #Has Access
        requestId = request.POST.get('requestid')
        if not logged_in(request):
            return _process_auth_response(request, "pyha")
        userRequest = Request.requests.get(id=requestId)        
        if not is_allowed_to_view(request, requestId):
            return HttpResponse('/pyha/', status=310)
        collectionId = request.POST.get('collectionId')
        requestId = request.POST.get('requestid')
        userRequest = Request.requests.get(id = requestId)
        collection = Collection.objects.get(id = collectionId)
        value = collection.taxonSecured + collection.customSecured
        collection.taxonSecured = 0
        collection.customSecured = 0
        collection.save(update_fields=['taxonSecured', 'customSecured'])
        if(collection.customSecured == 0) and (collection.status != -1):
            collection.status = -1
            collection.save(update_fields=['status'])
            userRequest = Request.requests.get(id = requestId)
            if(check_all_collections_removed(requestId)):
                return HttpResponse("/pyha/", status=310)
        context = create_request_view_context(requestId, request, userRequest)
        return HttpResponse("")
    return HttpResponse("")

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
        next = request.POST.get('next', '/')
        collectionId = request.POST.get('collectionId')
        requestId = request.POST.get('requestid')
        collection = Collection.objects.get(id = collectionId)
        collection.customSecured = 0
        collection.save(update_fields=['customSecured'])
        if(collection.taxonSecured == 0) and (collection.status != -1):
            collection.status = -1
            collection.save(update_fields=['status'])
            check_all_collections_removed(requestId)
        return HttpResponseRedirect(next)
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
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect('/pyha/')
        #avoid work when submitted multiple times
        if(collection.status != -1):
            collection.status = -1
            collection.save(update_fields=['status'])
            check_all_collections_removed(requestId)
        return HttpResponseRedirect(redirect_path)
    return HttpResponseRedirect("/pyha/")


def approve(request):
    if request.method == 'POST':
        if not logged_in(request):
            return _process_auth_response(request, "pyha")
        requestId = request.POST.get('requestid', '?')
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect('/pyha/')
        lang = 'fi' #ainakin toistaiseksi
        userRequest = Request.requests.get(id = requestId)
        requestedCollections = request.POST.getlist('checkb')
        senschecked = request.POST.get('checkbsens')
        collectionList = Collection.objects.filter(request=requestId, status__gte=0)
        if(userRequest.status == 0 and senschecked and len(collectionList) > 0):
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
                if not taxon:
                    userRequest.sensstatus = 4
                else:
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
            if userRequest.sensstatus == 1 and taxon:
                send_mail_for_approval_sens(requestId, lang)
            #make a log entry
            RequestLogEntry.requestLog.create(request=userRequest, user=request.session["user_id"], role=USER, action=RequestLogEntry.ACCEPT)
        else:
            userRequest.status = -1
            userRequest.save()
            RequestLogEntry.requestLog.create(request=userRequest, user=request.session["user_id"], role=USER, action=RequestLogEntry.ACCEPT)
    return HttpResponseRedirect('/pyha/')

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
