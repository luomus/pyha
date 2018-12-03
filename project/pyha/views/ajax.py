from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from pyha.database import create_request_view_context, check_all_collections_removed
from pyha.localization import check_language
from pyha.login import logged_in, is_allowed_to_view, is_request_owner, is_admin_frozen
from pyha.models import Request, Collection, StatusEnum, Sens_StatusEnum
from pyha.log_utils import changed_by_session_user

def get_description_ajax(request):
    if request.method == 'POST' and request.POST.get('requestid'):
        if check_language(request):
                return HttpResponse(reverse(request.get_full_path()), status=310)
        if not logged_in(request):
            return HttpResponse(reverse('pyha:root'), status=310)
        requestId = request.POST.get('requestid')
        if not is_allowed_to_view(request, requestId):
            return HttpResponse(reverse('pyha:root'), status=310)
        userRequest = Request.objects.get(id=requestId)
        context = create_request_view_context(requestId, request, userRequest)
        return render(request, 'pyha/base/ajax/requestheader.html', context)
    return HttpResponse(reverse('pyha:root'), status=310)

def set_description_ajax(request):
    if request.method == 'POST':
        if not logged_in(request):
            return HttpResponse(reverse('pyha:root'), status=310)
        requestId = request.POST.get('requestid')
        if not is_request_owner(request, requestId):
            return HttpResponse(reverse('pyha:root'), status=310)
        userRequest = Request.objects.get(id = requestId)
        if is_admin_frozen(request, userRequest):
            return HttpResponse(reverse('pyha:root'), status=310)
        userRequest.description = request.POST.get('description')
        userRequest.changedBy = changed_by_session_user(request)
        userRequest.save()
        return HttpResponse(status=200)
    return HttpResponse(reverse('pyha:root'), status=310)

def get_taxon_ajax(request):
    if request.method == 'POST' and request.POST.get('requestid'):
        if check_language(request):
                return HttpResponse(reverse(request.get_full_path()), status=310)
        if not logged_in(request):
            return HttpResponse(reverse('pyha:root'), status=310)
        requestId = request.POST.get('requestid')
        if not is_allowed_to_view(request, requestId):
            return HttpResponse(reverse('pyha:root'), status=310)
        userRequest = Request.objects.get(id=requestId)
        if is_admin_frozen(request, userRequest):
            return HttpResponse(reverse('pyha:root'), status=310)
        if(userRequest.status == StatusEnum.APPROVETERMS_WAIT):
            context = create_request_view_context(requestId, request, userRequest)
            return render(request, 'pyha/official/ajax/requestformtaxon.html', context)
    return HttpResponse(reverse('pyha:root'), status=310)
    
def get_custom_ajax(request):
    if request.method == 'POST' and request.POST.get('requestid'):
        if check_language(request):
                return HttpResponse(reverse(request.get_full_path()), status=310)
        if not logged_in(request):
            return HttpResponse(reverse('pyha:root'), status=310)
        requestId = request.POST.get('requestid')
        if not is_allowed_to_view(request, requestId):
            return HttpResponse(reverse('pyha:root'), status=310)
        userRequest = Request.objects.get(id=requestId)        
        if is_admin_frozen(request, userRequest):
            return HttpResponse(reverse('pyha:root'), status=310)
        if(userRequest.status == StatusEnum.APPROVETERMS_WAIT):
            context = create_request_view_context(requestId, request, userRequest)
            return render(request, 'pyha/official/ajax/requestformcustom.html', context)
    return HttpResponse(reverse('pyha:root'), status=310)

def get_collection_ajax(request):
    if request.method == 'POST' and request.POST.get('requestid'):
        if check_language(request):
                return HttpResponse(reverse(request.get_full_path()), status=310)
        if not logged_in(request):
            return HttpResponse(reverse('pyha:root'), status=310)
        requestId = request.POST.get('requestid') 
        if not is_allowed_to_view(request, requestId):
            return HttpResponse(reverse('pyha:root'), status=310)
        userRequest = Request.objects.get(id=requestId)   
        if is_admin_frozen(request, userRequest):
            return HttpResponse(reverse('pyha:root'), status=310)
        if(userRequest.status == StatusEnum.APPROVETERMS_WAIT):
            context = create_request_view_context(requestId, request, userRequest)
            return render(request, 'pyha/skipofficial/ajax/requestformcollection.html', context)
    return HttpResponse(reverse('pyha:root'), status=310)
    
def get_summary_ajax(request):
    if request.method == 'POST' and request.POST.get('requestid'):
        if check_language(request):
                return HttpResponse(reverse(request.get_full_path()), status=310)
        if not logged_in(request):
            return HttpResponse(reverse('pyha:root'), status=310)
        requestId = request.POST.get('requestid') 
        if not is_allowed_to_view(request, requestId):
            return HttpResponse(reverse('pyha:root'), status=310)
        userRequest = Request.objects.get(id=requestId)   
        if is_admin_frozen(request, userRequest):
            return HttpResponse(reverse('pyha:root'), status=310)
        if(userRequest.status == StatusEnum.APPROVETERMS_WAIT):
            context = create_request_view_context(requestId, request, userRequest)
            if userRequest.sensStatus == Sens_StatusEnum.IGNORE_OFFICIAL:
                return render(request, 'pyha/skipofficial/ajax/requestformsummary.html', context)
            else:
                return render(request, 'pyha/official/ajax/requestformsummary.html', context)
    return HttpResponse(reverse('pyha:root'), status=310)

def create_contact_ajax(request):
    if request.method == 'POST' and request.POST.get('requestid') and request.POST.get('id'):
        if check_language(request):
                return HttpResponse(reverse(request.get_full_path()), status=310)
        if not logged_in(request):
            return HttpResponse(reverse('pyha:root'), status=310)
        requestId = request.POST.get('requestid') 
        if not is_request_owner(request, requestId):
            return HttpResponse(reverse('pyha:root'), status=310)
        userRequest = Request.objects.get(id=requestId)   
        if is_admin_frozen(request, userRequest):
            return HttpResponse(reverse('pyha:root'), status=310)
        if(userRequest.status == StatusEnum.APPROVETERMS_WAIT):
            context = create_request_view_context(requestId, request, userRequest)
            context["contact_id"] = request.POST.get('id')
            return render(request, 'pyha/base/ajax/requestformcontact.xml', context)
    return HttpResponse(reverse('pyha:root'), status=310)

def remove_collection_ajax(request):
    if request.method == 'POST' and request.POST.get('requestid'):
        if check_language(request):
                return HttpResponse(reverse(request.get_full_path()), status=310)
        if not logged_in(request):
            return HttpResponse(reverse('pyha:root'), status=310)
        requestId = request.POST.get('requestid') 
        if not is_request_owner(request, requestId):
            return HttpResponse(reverse('pyha:root'), status=310)
        userRequest = Request.objects.get(id=requestId)   
        if is_admin_frozen(request, userRequest):
            return HttpResponse(reverse('pyha:root'), status=310)
        collectionId = request.POST.get('collectionId')
        collection = Collection.objects.get(id = collectionId)
        if(userRequest.status == StatusEnum.APPROVETERMS_WAIT and collection.status != -1):
            collection.status = -1
            collection.changedBy = changed_by_session_user(request)
            collection.save()
            if(check_all_collections_removed(requestId)):
                return HttpResponse(reverse('pyha:root'), status=310)
            return HttpResponse(status=200)
    return HttpResponse(reverse('pyha:root'), status=310)
