from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from pyha.database import create_request_view_context, check_all_collections_removed
from pyha.localization import check_language
from pyha.login import logged_in, is_allowed_to_view, is_request_owner
from pyha.models import Request, Collection

def get_description_ajax(request):
    if request.method == 'POST' and request.POST.get('requestid'):
        if check_language(request):
                return HttpResponseRedirect(request.get_full_path())
        if not logged_in(request):
            return HttpResponseRedirect(reverse('pyha:index'))
        requestId = request.POST.get('requestid')
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect(reverse('pyha:index'))
        userRequest = Request.objects.get(id=requestId)
        context = create_request_view_context(requestId, request, userRequest)
        return render(request, 'pyha/requestheader.html', context)
    return HttpResponseRedirect(reverse('pyha:index'))

def set_description_ajax(request):
    if request.method == 'POST':
        if not logged_in(request):
            return HttpResponseRedirect(reverse('pyha:index'))
        requestId = request.POST.get('requestid')
        if not is_request_owner(request, requestId):
            return HttpResponseRedirect(reverse('pyha:index'))
        userRequest = Request.objects.get(id = requestId)
        userRequest.description = request.POST.get('description')
        userRequest.save(update_fields=['description'])
        return HttpResponse(status=200)
    return HttpResponseRedirect(reverse('pyha:index'))

def get_taxon_ajax(request):
    if request.method == 'POST' and request.POST.get('requestid'):
        if check_language(request):
                return HttpResponseRedirect(request.get_full_path())
        if not logged_in(request):
            return HttpResponseRedirect(reverse('pyha:index'))
        requestId = request.POST.get('requestid')
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect(reverse('pyha:index'))
        userRequest = Request.objects.get(id=requestId)
        context = create_request_view_context(requestId, request, userRequest)
        return render(request, 'pyha/requestformtaxon.html', context)
    return HttpResponse(reverse('pyha:index'), status=310)
    
def get_custom_ajax(request):
    if request.method == 'POST' and request.POST.get('requestid'):
        if check_language(request):
                return HttpResponseRedirect(request.get_full_path())
        if not logged_in(request):
            return HttpResponseRedirect(reverse('pyha:index'))
        requestId = request.POST.get('requestid')
        userRequest = Request.objects.get(id=requestId)        
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect(reverse('pyha:index'))
        context = create_request_view_context(requestId, request, userRequest)
        return render(request, 'pyha/requestformcustom.html', context)
    return HttpResponseRedirect(reverse('pyha:index'))

def get_collection_ajax(request):
    if request.method == 'POST' and request.POST.get('requestid'):
        if check_language(request):
                return HttpResponseRedirect(request.get_full_path())
        if not logged_in(request):
            return HttpResponseRedirect(reverse('pyha:index'))
        requestId = request.POST.get('requestid') 
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect(reverse('pyha:index'))
        userRequest = Request.objects.get(id=requestId)   
        context = create_request_view_context(requestId, request, userRequest)
        return render(request, 'pyha/skipofficial/requestformcollection.html', context)
    return HttpResponseRedirect(reverse('pyha:index'))
    
def get_summary_ajax(request):
    if request.method == 'POST' and request.POST.get('requestid'):
        if check_language(request):
                return HttpResponseRedirect(request.get_full_path())
        if not logged_in(request):
            return HttpResponseRedirect(reverse('pyha:index'))
        requestId = request.POST.get('requestid') 
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect(reverse('pyha:index'))
        userRequest = Request.objects.get(id=requestId)   
        context = create_request_view_context(requestId, request, userRequest)
        return render(request, 'pyha/requestformsummary.html', context)
    return HttpResponseRedirect(reverse('pyha:index'))

def create_contact_ajax(request):
    if request.method == 'POST' and request.POST.get('requestid') and request.POST.get('id'):
        if check_language(request):
                return HttpResponseRedirect(request.get_full_path())
        if not logged_in(request):
            return HttpResponseRedirect(reverse('pyha:index'))
        requestId = request.POST.get('requestid') 
        if not is_request_owner(request, requestId):
            return HttpResponseRedirect(reverse('pyha:index'))
        userRequest = Request.objects.get(id=requestId)   
        context = create_request_view_context(requestId, request, userRequest)
        context["contact_id"] = request.POST.get('id')
        return render(request, 'pyha/requestformcontact.xml', context)
    return HttpResponseRedirect(reverse('pyha:index'))

def remove_collection_ajax(request):
    if request.method == 'POST' and request.POST.get('requestid'):
        if check_language(request):
                return HttpResponseRedirect(request.get_full_path())
        if not logged_in(request):
            return HttpResponseRedirect(reverse('pyha:index'))
        requestId = request.POST.get('requestid') 
        if not is_request_owner(request, requestId):
            return HttpResponseRedirect(reverse('pyha:index'))
        collectionId = request.POST.get('collectionId')
        collection = Collection.objects.get(id = collectionId)
        if(collection.status != -1):
            collection.status = -1
            collection.save(update_fields=['status'])
            if(check_all_collections_removed(requestId)):
                return HttpResponse(reverse('pyha:index'), status=310)
    return HttpResponseRedirect(reverse('pyha:index'))
