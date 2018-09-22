import json

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from pyha.database import create_request_view_context, check_all_collections_removed, create_new_contact, update_contact_preset
from pyha.email import send_mail_for_approval, send_mail_for_approval_sens
from pyha.localization import check_language
from pyha.login import logged_in, _process_auth_response, is_allowed_to_view
from pyha.models import RequestLogEntry, Request, Collection
from pyha.roles import USER


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

def get_collection(request):
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
        return render(request, 'pyha/skipofficial/requestformcollection.html', context)
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
        return HttpResponseRedirect('/b/')
    return HttpResponseRedirect('/a/')

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
