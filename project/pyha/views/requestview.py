from datetime import datetime
import os

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pyha.database import create_request_view_context, make_logEntry_view, update, ignore_official_update, target_valid
from pyha.email import send_mail_after_additional_information_requested
from pyha.localization import check_language
from pyha.login import logged_in, _process_auth_response, is_allowed_to_view, is_allowed_to_handle
from pyha.models import RequestLogEntry, RequestChatEntry, RequestInformationChatEntry, Request, Collection
from pyha.roles import HANDLER_ANY, HANDLER_SENS, HANDLER_COLL
from pyha.warehouse import send_download_request


def get_request_header(request):
    if request.method == 'POST' and request.POST.get('requestid'):
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
        return render(request, 'pyha/requestheader.html', context)
    return HttpResponse("")

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
        userRole = request.session["current_user_role"]
        #make a log entry
        userId = request.session["user_id"]
        if userRequest.user != userId:
            role1 = HANDLER_SENS in request.session.get("user_roles", [None])
            role2 = HANDLER_COLL in request.session.get("user_roles", [None])
            make_logEntry_view(request, userRequest, userId, role1, role2)
        context = create_request_view_context(requestId, request, userRequest)
        if HANDLER_ANY in request.session.get("current_user_role", [None]):
            return render(request, 'pyha/skipofficial/requestview_handler.html', context) if userRequest.sensstatus == 99 else render(request, 'pyha/handler/requestview.html', context)
        else:
            if(userRequest.status == 0):
                result = render(request, 'pyha/skipofficial/requestform.html', context) if userRequest.sensstatus == 99 else render(request, 'pyha/requestform.html', context)
                return result
            else:
                return render(request, 'pyha/skipofficial/requestview.html', context)  if userRequest.sensstatus == 99 else render(request, 'pyha/requestview.html', context)
    
def change_description_ajax(request):
    if request.method == 'POST':
        if not logged_in(request):
            return _process_auth_response(request, "pyha")
        next = request.POST.get('next', '/')
        requestId = request.POST.get('requestid')
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect('/pyha/')
        userRequest = Request.requests.get(id = requestId)
        userRequest.description = request.POST.get('description')
        userRequest.save(update_fields=['description'])
        return HttpResponse(status=200)
    return HttpResponseRedirect('/pyha/')

def comment_sensitive(request):
        next = request.POST.get('next', '/')
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
        return HttpResponseRedirect(next)
    
def initialize_download(request):
        next = request.POST.get('next', '/')
        if request.method == 'POST':
            if not logged_in(request):
                return _process_auth_response(request, "pyha")
            requestId = request.POST.get('requestid', '?')
            if not is_allowed_to_view(request, requestId):
                return HttpResponseRedirect('/pyha/')
            userRequest = Request.requests.get(id=requestId)
            if (userRequest.status == 4 or userRequest.status == 2 or userRequest.sensstatus == 4):
                send_download_request(requestId)
                userRequest.status = 7
                userRequest.save()
        return HttpResponseRedirect(next)
    
def change_description(request):
    if request.method == 'POST':
        if not logged_in(request):
            return _process_auth_response(request, "pyha")
        next = request.POST.get('next', '/')
        requestId = request.POST.get('requestid')
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect('/pyha/')
        userRequest = Request.requests.get(id = requestId)
        userRequest.description = request.POST.get('description')
        userRequest.save(update_fields=['description'])
        return HttpResponseRedirect(next)
    return HttpResponseRedirect('/pyha/')

def answer(request):
        next = request.POST.get('next', '/')
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
                if not is_allowed_to_handle(request, target, requestId):
                    return HttpResponseRedirect('/pyha/')
                newChatEntry = RequestInformationChatEntry()
                newChatEntry.request = Request.requests.get(id=requestId)
                newChatEntry.date = datetime.now()
                newChatEntry.user = request.session["user_id"]
                newChatEntry.question = True
                newChatEntry.target = target
                newChatEntry.message = request.POST.get('reason')
                newChatEntry.save()
                userRequest.status = 6
                userRequest.save()
                send_mail_after_additional_information_requested(requestId, request.LANGUAGE_CODE)
            elif "sens" not in collectionId:
                collection = Collection.objects.get(request=requestId, address=collectionId)
                if (request.session["user_id"] in collection.downloadRequestHandler) and userRequest.status != 7 and userRequest.status != 8 and userRequest.status != 3:
                    if (int(request.POST.get('answer')) == 1):
                        collection.status = 4
                        #make a log entry
                        RequestLogEntry.requestLog.create(request = Request.requests.get(id = requestId), collection = collection, user = request.session["user_id"], role = HANDLER_COLL, action =RequestLogEntry.DECISION_POSITIVE)
                    else:
                        collection.status = 3
                        #make a log entry
                        RequestLogEntry.requestLog.create(request = Request.requests.get(id = requestId),collection = collection, user = request.session["user_id"], role = HANDLER_COLL, action =RequestLogEntry.DECISION_NEGATIVE)
                    collection.decisionExplanation = request.POST.get('reason')
                    collection.save()
                    if userRequest.sensstatus == 99:
                        ignore_official_update(requestId, request.LANGUAGE_CODE) 
                    else: 
                        update(requestId, request.LANGUAGE_CODE)
            elif HANDLER_SENS in request.session["user_roles"]:
                if (int(request.POST.get('answer')) == 1):
                    userRequest.sensstatus = 4
                    #make a log entry
                    RequestLogEntry.requestLog.create(request = Request.requests.get(id = requestId), user = request.session["user_id"], role = HANDLER_SENS, action = RequestLogEntry.DECISION_POSITIVE)
                else:
                    userRequest.sensstatus = 3
                    #make a log entry
                    RequestLogEntry.requestLog.create(request = Request.requests.get(id = requestId), user = request.session["user_id"], role = HANDLER_SENS, action = RequestLogEntry.DECISION_NEGATIVE)
                userRequest.sensDecisionExplanation = request.POST.get('reason')
                userRequest.save()
                update(requestId, request.LANGUAGE_CODE)
        return HttpResponseRedirect(next)

def information(request):
        next = request.POST.get('next', '/')
        if request.method == 'POST':
            if not logged_in(request):
                return _process_auth_response(request, "pyha")
            requestId = request.POST.get('requestid', '?')
            target = request.POST.get('target', '?')
            if not is_allowed_to_view(request, requestId):
                return HttpResponseRedirect('/pyha/')
            if(int(request.POST.get('information')) == 2):
                if not target_valid(request, target, requestId):
                    return HttpResponseRedirect('/pyha/')
                newChatEntry = RequestInformationChatEntry()
                newChatEntry.request = Request.requests.get(id=requestId)
                newChatEntry.date = datetime.now()
                newChatEntry.user = request.session["user_id"]
                newChatEntry.question = False
                newChatEntry.target = target
                newChatEntry.message = request.POST.get('reason')
                newChatEntry.save()
                userRequest = Request.requests.get(id = requestId)
                userRequest.status = 1
                userRequest.save()
                update(requestId, request.LANGUAGE_CODE)
        return HttpResponseRedirect(next)