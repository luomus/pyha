from datetime import datetime
import os

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pyha.database import create_request_view_context, make_logEntry_view, update_request_status, target_valid
from pyha.email import send_mail_after_additional_information_requested
from pyha.localization import check_language
from pyha.login import logged_in, _process_auth_response, is_allowed_to_view, add_sensitive_handler_roles
from pyha.models import RequestLogEntry, RequestChatEntry, RequestInformationChatEntry, Request, Collection, StatusEnum
from pyha.roles import HANDLER_ANY, HANDLER_SENS, HANDLER_COLL
from pyha.warehouse import send_download_request, is_download_handler_in_collection

@csrf_exempt
def show_request(request):
    if check_language(request):
        return HttpResponseRedirect(request.get_full_path())
    #Has Access
    requestId = os.path.basename(os.path.normpath(request.path))
    if not logged_in(request):
        return _process_auth_response(request, "request/"+requestId)
    if not is_allowed_to_view(request, requestId):
        return HttpResponseRedirect('/pyha/')
    userRequest = Request.requests.get(id=requestId)
    #make a log entry
    userId = request.session["user_id"]
    if userRequest.user != userId:
        role1 = HANDLER_SENS in request.session.get("user_roles", [None])
        role2 = HANDLER_COLL in request.session.get("user_roles", [None])
        make_logEntry_view(request, userRequest, userId, role1, role2)
    context = create_request_view_context(requestId, request, userRequest)
    if HANDLER_ANY in request.session.get("current_user_role", [None]):
        return render(request, 'pyha/skipofficial/requestview_handler.html', context) if userRequest.sensstatus == StatusEnum.IGNORE_OFFICIAL else render(request, 'pyha/handler/requestview.html', context)
    else:
        if(userRequest.status == 0):
            result = render(request, 'pyha/skipofficial/requestform.html', context) if userRequest.sensstatus == StatusEnum.IGNORE_OFFICIAL else render(request, 'pyha/requestform.html', context)
            return result
        else:
            return render(request, 'pyha/skipofficial/requestview.html', context)  if userRequest.sensstatus == StatusEnum.IGNORE_OFFICIAL else render(request, 'pyha/requestview.html', context)
    
def comment_sensitive(request):
    nexturl = request.POST.get('next', '/')
    if request.method == 'POST':
        if not logged_in(request):
            return _process_auth_response(request, "pyha")
        requestId = request.POST.get('requestid', '?')
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect('/pyha/')
        message = request.POST.get('commentsForAuthorities')
        if HANDLER_SENS in request.session["user_roles"]:
            newChatEntry = RequestChatEntry()
            newChatEntry.request = Request.requests.get(id=requestId)
            newChatEntry.date = datetime.now()
            newChatEntry.user = request.session["user_id"]
            newChatEntry.message = message
            newChatEntry.save()
    return HttpResponseRedirect(nexturl)
    
def initialize_download(request):
    nexturl = request.POST.get('next', '/')
    if request.method == 'POST':
        if not logged_in(request):
            return _process_auth_response(request, "pyha")
        requestId = request.POST.get('requestid', '?')
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect('/pyha/')
        userRequest = Request.requests.get(id=requestId)
        if (userRequest.status == 4 or userRequest.status == 2 or userRequest.sensstatus == 4 or userRequest.sensstatus == 99):
            send_download_request(requestId)
            userRequest.status = 7
            userRequest.save()
    return HttpResponseRedirect(nexturl)
    
def change_description(request):
    if request.method == 'POST':
        if not logged_in(request):
            return _process_auth_response(request, "pyha")
        nexturl = request.POST.get('next', '/')
        requestId = request.POST.get('requestid')
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect('/pyha/')
        userRequest = Request.requests.get(id = requestId)
        userRequest.description = request.POST.get('description')
        userRequest.save(update_fields=['description'])
        return HttpResponseRedirect(nexturl)
    return HttpResponseRedirect('/pyha/')

def answer(request):
    nexturl = request.POST.get('next', '/')
    if request.method == 'POST':
        if not logged_in(request):
            return _process_auth_response(request, "pyha")
        requestId = request.POST.get('requestid', '?')
        target = request.POST.get('target', '?')
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect('/pyha/')
        collectionId = request.POST.get('collectionid')
        userRequest = Request.requests.get(id = requestId)
        if(int(request.POST.get('answer')) == 2):
            if not add_sensitive_handler_roles(request, target, requestId):
                return HttpResponseRedirect('/pyha/')
            newChatEntry = RequestInformationChatEntry()
            newChatEntry.request = Request.requests.get(id=requestId)
            newChatEntry.date = datetime.now()
            newChatEntry.user = request.session["user_id"]
            newChatEntry.question = True
            newChatEntry.target = target
            newChatEntry.message = request.POST.get('reason')
            newChatEntry.save()
            userRequest.status = StatusEnum.WAITING_FOR_INFORMATION
            userRequest.save()
            send_mail_after_additional_information_requested(requestId, request.LANGUAGE_CODE)
        elif "sens" not in collectionId:
            collection = Collection.objects.get(request=requestId, address=collectionId)
            #if (request.session["user_id"] in collection.downloadRequestHandler) and userRequest.status != 7 and userRequest.status != 8 and userRequest.status != 3:
            if is_download_handler_in_collection(request.session["user_id"], collectionId) and userRequest.status != 7 and userRequest.status != 8 and userRequest.status != 3:
                if (int(request.POST.get('answer')) == 1):
                    collection.status = StatusEnum.APPROVED
                    #make a log entry
                    RequestLogEntry.requestLog.create(request = Request.requests.get(id = requestId), collection = collection, user = request.session["user_id"], role = HANDLER_COLL, action= RequestLogEntry.DECISION_POSITIVE)
                else:
                    collection.status = StatusEnum.REJECTED
                    #make a log entry
                    RequestLogEntry.requestLog.create(request = Request.requests.get(id = requestId),collection = collection, user = request.session["user_id"], role = HANDLER_COLL, action = RequestLogEntry.DECISION_NEGATIVE)
                collection.decisionExplanation = request.POST.get('reason')
                collection.save()
                update_request_status(userRequest, request.LANGUAGE_CODE)
        elif HANDLER_SENS in request.session["user_roles"]:
            collections = Collection.objects.filter(request=requestId, customSecured__lte = 0, taxonSecured__gt=0, status__gte = 0)
            if (int(request.POST.get('answer')) == 1):
                userRequest.sensstatus = StatusEnum.APPROVED
                for co in collections:
                    co.status =  StatusEnum.APPROVED
                #make a log entry
                RequestLogEntry.requestLog.create(request = Request.requests.get(id = requestId), user = request.session["user_id"], role = HANDLER_SENS, action = RequestLogEntry.DECISION_POSITIVE)
            else:
                userRequest.sensstatus = StatusEnum.REJECTED
                for co in collections:
                    co.status =  StatusEnum.REJECTED
                #make a log entry
                RequestLogEntry.requestLog.create(request = Request.requests.get(id = requestId), user = request.session["user_id"], role = HANDLER_SENS, action = RequestLogEntry.DECISION_NEGATIVE)
            userRequest.sensDecisionExplanation = request.POST.get('reason')
            userRequest.save()
            update_request_status(userRequest, request.LANGUAGE_CODE)
    return HttpResponseRedirect(nexturl)
    

def information(request):
    nexturl = request.POST.get('next', '/')
    if request.method == 'POST':
        if not logged_in(request):
            return _process_auth_response(request, "pyha")
        requestId = request.POST.get('requestid', '?')
        target = request.POST.get('target', '?')
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect('/pyha/')
        if(int(request.POST.get('information')) == 2):
            if not target_valid(target, requestId):
                return HttpResponseRedirect('/pyha/')
            userRequest = Request.requests.get(id = requestId)
            newChatEntry = RequestInformationChatEntry()
            newChatEntry.request = userRequest
            newChatEntry.date = datetime.now()
            newChatEntry.user = request.session["user_id"]
            newChatEntry.question = False
            newChatEntry.target = target
            newChatEntry.message = request.POST.get('reason')
            newChatEntry.save() 
            userRequest.status = StatusEnum.WAITING
            for co in Collection.objects.filter(request = userRequest):
                try:
                    if RequestInformationChatEntry.objects.filter(request=userRequest, target=co.address).latest('date').question: 
                        userRequest.status = StatusEnum.WAITING_FOR_INFORMATION
                        break
                except RequestInformationChatEntry.DoesNotExist:
                    pass        
            try:
                if RequestInformationChatEntry.objects.filter(request=userRequest, target="sens").latest('date').question:
                    userRequest.status = StatusEnum.WAITING_FOR_INFORMATION           
            except RequestInformationChatEntry.DoesNotExist:
                pass        
            userRequest.save()
            update_request_status(userRequest, request.LANGUAGE_CODE)
    return HttpResponseRedirect(nexturl)