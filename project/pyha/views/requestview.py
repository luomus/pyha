from datetime import datetime
import os

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from pyha.database import create_request_view_context, make_logEntry_view, update_request_status, target_valid, contains_approved_collection
from pyha.email import send_mail_after_additional_information_requested
from pyha.localization import check_language
from pyha.login import logged_in, _process_auth_response, is_allowed_to_view, is_request_owner, is_admin_frozen_and_not_admin, is_allowed_to_ask_information_as_target, is_admin
from pyha.models import RequestLogEntry, RequestSensitiveChatEntry, RequestHandlerChatEntry, RequestInformationChatEntry, Request, Collection, StatusEnum, Sens_StatusEnum, Col_StatusEnum
from pyha.roles import HANDLER_ANY, CAT_HANDLER_SENS, CAT_HANDLER_COLL, ADMIN, CAT_ADMIN
from pyha.warehouse import send_download_request, is_download_handler_in_collection
from pyha.log_utils import changed_by_session_user
from pyha import toast

@csrf_exempt
def show_request(request):
    if check_language(request):
        return HttpResponseRedirect(request.get_full_path())
    #Has Access
    requestId = os.path.basename(os.path.normpath(request.path))
    if not logged_in(request):
        return _process_auth_response(request, "request/"+requestId)
    if not is_allowed_to_view(request, requestId):
        return HttpResponseRedirect(reverse('pyha:root'))
    userRequest = Request.objects.get(id=requestId)
    if is_admin_frozen_and_not_admin(request, userRequest):
        return HttpResponseRedirect(reverse('pyha:root'))
    userId = request.session["user_id"]
    if userRequest.user != userId:
        role1 = CAT_HANDLER_SENS in request.session.get("user_roles", [None])
        role2 = CAT_HANDLER_COLL in request.session.get("user_roles", [None])
        role3 = CAT_ADMIN in request.session.get("user_roles", [None])
        #make a log entry
        make_logEntry_view(request, userRequest, userId, role1, role2, role3)
    context = create_request_view_context(requestId, request, userRequest)
    if ADMIN in request.session.get("current_user_role", [None]):
        update_request_status(userRequest, userRequest.lang)
        return render(request, 'pyha/skipofficial/admin/requestview.html', context) if userRequest.sensStatus == Sens_StatusEnum.IGNORE_OFFICIAL else render(request, 'pyha/official/admin/requestview.html', context)
    else:
        if HANDLER_ANY in request.session.get("current_user_role", [None]):
            update_request_status(userRequest, userRequest.lang)
            return render(request, 'pyha/skipofficial/handler/requestview.html', context) if userRequest.sensStatus == Sens_StatusEnum.IGNORE_OFFICIAL else render(request, 'pyha/official/handler/requestview.html', context)
        else:
            if(userRequest.status == 0):
                return render(request, 'pyha/skipofficial/requestform.html', context) if userRequest.sensStatus == Sens_StatusEnum.IGNORE_OFFICIAL else render(request, 'pyha/official/requestform.html', context)
            else:
                update_request_status(userRequest, userRequest.lang)
                return render(request, 'pyha/skipofficial/requestview.html', context)  if userRequest.sensStatus == Sens_StatusEnum.IGNORE_OFFICIAL else render(request, 'pyha/official/requestview.html', context)
    
def comment_sensitive(request):
    nexturl = request.POST.get('next', '/')
    if request.method == 'POST':
        if not logged_in(request):
            return _process_auth_response(request, "pyha")
        requestId = request.POST.get('requestid', '?')
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        message = request.POST.get('commentsForAuthorities')
        userRequest = Request.objects.get(id=requestId) 
        if is_admin_frozen_and_not_admin(request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        if CAT_HANDLER_SENS in request.session["user_roles"] and not userRequest.sensStatus == Sens_StatusEnum.IGNORE_OFFICIAL:
            newChatEntry = RequestSensitiveChatEntry()
            newChatEntry.request = userRequest
            newChatEntry.date = datetime.now()
            newChatEntry.user = request.session["user_id"]
            newChatEntry.message = message
            newChatEntry.changedBy = changed_by_session_user(request)
            newChatEntry.save()
    return HttpResponseRedirect(nexturl)

def comment_handler(request):
    nexturl = request.POST.get('next', '/')
    if request.method == 'POST':
        requestId = request.POST.get('requestid', '?')
        target = request.POST.get('target', '?')
        message = request.POST.get('commentsForHandlers')
        if not logged_in(request):
            return _process_auth_response(request, "pyha")
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        userRequest = Request.objects.get(id=requestId) 
        if is_admin_frozen_and_not_admin(request, userRequest):
            return HttpResponseRedirect(reverse('pyha:root'))
        if is_allowed_to_ask_information_as_target(request,target,requestId):
            newChatEntry = RequestHandlerChatEntry()
            newChatEntry.request = userRequest
            newChatEntry.target = target
            newChatEntry.date = datetime.now()
            newChatEntry.user = request.session["user_id"]
            newChatEntry.message = message
            newChatEntry.changedBy = changed_by_session_user(request)
            newChatEntry.save()
    return HttpResponseRedirect(nexturl)
    
def initialize_download(request):
    nexturl = request.POST.get('next', '/')
    if request.method == 'POST':
        requestId = request.POST.get('requestid', '?')
        if not logged_in(request):
            return _process_auth_response(request, "pyha")
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        if not is_request_owner(request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        userRequest = Request.objects.get(id=requestId) 
        if is_admin_frozen_and_not_admin(request, userRequest):
            return HttpResponseRedirect(reverse('pyha:root'))
        if(not userRequest.frozen or ADMIN in request.session["current_user_role"]):
            if (userRequest.status == 4 or userRequest.status == 2 or (userRequest.sensStatus in [4,99] and contains_approved_collection(requestId))):
                send_download_request(requestId)
                userRequest.status = 7
                userRequest.changedBy = changed_by_session_user(request)
                userRequest.save()
    return HttpResponseRedirect(nexturl)
    
def change_description(request):
    if request.method == 'POST':
        nexturl = request.POST.get('next', '/')
        requestId = request.POST.get('requestid')
        if not logged_in(request):
            return _process_auth_response(request, "pyha")
        if not is_request_owner(request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        userRequest = Request.objects.get(id = requestId)
        if is_admin_frozen_and_not_admin(request, userRequest):
            return HttpResponseRedirect(reverse('pyha:root'))
        userRequest.description = request.POST.get('description')
        userRequest.changedBy = changed_by_session_user(request)
        userRequest.save()
        return HttpResponseRedirect(nexturl)
    return HttpResponseRedirect(reverse('pyha:root'))

def freeze(request):
    if request.method == 'POST':
        nexturl = request.POST.get('next', '/')
        requestId = request.POST.get('requestid')
        if not logged_in(request):
            return _process_auth_response(request, "pyha")
        if not is_admin(request):
            return HttpResponse(status=404)
        userRequest = Request.objects.get(id = requestId)
        if userRequest.frozen: userRequest.frozen = False
        else: userRequest.frozen = True
        userRequest.changedBy = changed_by_session_user(request)
        userRequest.save()
        return HttpResponseRedirect(nexturl)
    return HttpResponse(status=404)

def answer(request):
    nexturl = request.POST.get('next', '/')
    if request.method == 'POST':
        if not logged_in(request):
            return _process_auth_response(request, "pyha")
        requestId = request.POST.get('requestid', '?')
        target = request.POST.get('target', '?')
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        collectionId = request.POST.get('collectionid')
        userRequest = Request.objects.get(id = requestId)
        if is_admin_frozen_and_not_admin(request, userRequest):
            return HttpResponseRedirect(reverse('pyha:root'))
        if(int(request.POST.get('answer')) == 2):
            if not is_allowed_to_ask_information_as_target(request, target, requestId):
                return HttpResponseRedirect(reverse('pyha:root'))
            newChatEntry = RequestInformationChatEntry()
            newChatEntry.request = Request.objects.get(id=requestId)
            newChatEntry.date = datetime.now()
            newChatEntry.user = request.session["user_id"]
            newChatEntry.question = True
            newChatEntry.target = target
            newChatEntry.message = request.POST.get('reason')
            newChatEntry.changedBy = changed_by_session_user(request)
            newChatEntry.save()
            userRequest.status = StatusEnum.WAITING_FOR_INFORMATION
            userRequest.changedBy = changed_by_session_user(request)
            userRequest.save()
            send_mail_after_additional_information_requested(requestId, request.LANGUAGE_CODE)
        elif ADMIN in request.session["current_user_role"]:
            if "sens" not in collectionId:
                collection = Collection.objects.get(request=requestId, address=collectionId)
                if (int(request.POST.get('answer')) == 1):
                    collection.status = Col_StatusEnum.APPROVED
                    #make a log entry
                    RequestLogEntry.requestLog.create(request = Request.objects.get(id = requestId), collection = collection, user = request.session["user_id"], role = CAT_ADMIN, action = RequestLogEntry.DECISION_POSITIVE)
                elif (int(request.POST.get('answer')) == 3):                    
                    collection.status = Col_StatusEnum.WAITING
                    #make a log entry
                    RequestLogEntry.requestLog.create(request = Request.objects.get(id = requestId), collection = collection, user = request.session["user_id"], role = CAT_ADMIN, action = RequestLogEntry.DECISION_RESET)
                else:
                    collection.status = Col_StatusEnum.REJECTED
                    #make a log entry
                    RequestLogEntry.requestLog.create(request = Request.objects.get(id = requestId),collection = collection, user = request.session["user_id"], role = CAT_ADMIN, action = RequestLogEntry.DECISION_NEGATIVE)
                collection.decisionExplanation = request.POST.get('reason')
                collection.changedBy = changed_by_session_user(request)
                collection.save()
                update_request_status(userRequest, userRequest.lang)
            elif userRequest.sensStatus != Sens_StatusEnum.IGNORE_OFFICIAL:
                collections = Collection.objects.filter(request=requestId, customSecured__lte = 0, taxonSecured__gt=0, status__gte = 0)
                if (int(request.POST.get('answer')) == 1):
                    userRequest.sensStatus = Sens_StatusEnum.APPROVED
                    for co in collections:
                        co.status =  Col_StatusEnum.APPROVED
                    #make a log entry
                    RequestLogEntry.requestLog.create(request = Request.objects.get(id = requestId), user = request.session["user_id"], role = CAT_ADMIN, action = RequestLogEntry.DECISION_POSITIVE)
                elif (int(request.POST.get('answer')) == 3):                    
                    userRequest.sensStatus = Sens_StatusEnum.WAITING
                    for co in collections:
                        co.status =  Col_StatusEnum.WAITING
                    #make a log entry
                    RequestLogEntry.requestLog.create(request = Request.objects.get(id = requestId), collection = collection, user = request.session["user_id"], role = CAT_ADMIN, action = RequestLogEntry.DECISION_RESET)
                else:
                    userRequest.sensStatus = Sens_StatusEnum.REJECTED
                    for co in collections:
                        co.status =  Col_StatusEnum.REJECTED
                    #make a log entry
                    RequestLogEntry.requestLog.create(request = Request.objects.get(id = requestId), user = request.session["user_id"], role = CAT_ADMIN, action = RequestLogEntry.DECISION_NEGATIVE)
                userRequest.sensDecisionExplanation = request.POST.get('reason')
                userRequest.changedBy = changed_by_session_user(request)
                userRequest.save()
                update_request_status(userRequest, userRequest.lang)
        elif HANDLER_ANY == request.session["current_user_role"]:
            if "sens" not in collectionId:
                collection = Collection.objects.get(request=requestId, address=collectionId)
                #if (request.session["user_id"] in collection.downloadRequestHandler) and userRequest.status != 7 and userRequest.status != 8 and userRequest.status != 3:
                if is_download_handler_in_collection(request.session["user_id"], collectionId) and userRequest.status != 7 and userRequest.status != 8 and userRequest.status != 3:
                    if (int(request.POST.get('answer')) == 1):
                        collection.status = Col_StatusEnum.APPROVED
                        #make a log entry
                        RequestLogEntry.requestLog.create(request = Request.objects.get(id = requestId), collection = collection, user = request.session["user_id"], role = CAT_HANDLER_COLL, action = RequestLogEntry.DECISION_POSITIVE)
                    else:
                        collection.status = Col_StatusEnum.REJECTED
                        #make a log entry
                        RequestLogEntry.requestLog.create(request = Request.objects.get(id = requestId),collection = collection, user = request.session["user_id"], role = CAT_HANDLER_COLL, action = RequestLogEntry.DECISION_NEGATIVE)
                    collection.decisionExplanation = request.POST.get('reason')
                    collection.changedBy = changed_by_session_user(request)
                    collection.save()
                    update_request_status(userRequest, userRequest.lang)
            elif CAT_HANDLER_SENS in request.session["user_roles"] and userRequest.sensStatus != Sens_StatusEnum.IGNORE_OFFICIAL:
                collections = Collection.objects.filter(request=requestId, customSecured__lte = 0, taxonSecured__gt=0, status__gte = 0)
                if (int(request.POST.get('answer')) == 1):
                    userRequest.sensStatus = Sens_StatusEnum.APPROVED
                    for co in collections:
                        co.status =  Col_StatusEnum.APPROVED
                    #make a log entry
                    RequestLogEntry.requestLog.create(request = Request.objects.get(id = requestId), user = request.session["user_id"], role = CAT_HANDLER_SENS, action = RequestLogEntry.DECISION_POSITIVE)
                else:
                    userRequest.sensStatus = Sens_StatusEnum.REJECTED
                    for co in collections:
                        co.status =  Col_StatusEnum.REJECTED
                    #make a log entry
                    RequestLogEntry.requestLog.create(request = Request.objects.get(id = requestId), user = request.session["user_id"], role = CAT_HANDLER_SENS, action = RequestLogEntry.DECISION_NEGATIVE)
                userRequest.sensDecisionExplanation = request.POST.get('reason')
                userRequest.changedBy = changed_by_session_user(request)
                userRequest.save()
                update_request_status(userRequest, userRequest.lang)
    return HttpResponseRedirect(nexturl)
    

def information(request):
    nexturl = request.POST.get('next', '/')
    if request.method == 'POST':
        if not logged_in(request):
            return _process_auth_response(request, "pyha")
        requestId = request.POST.get('requestid', '?')
        target = request.POST.get('target', '?')
        if not is_allowed_to_view(request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        userRequest = Request.objects.get(id = requestId)
        if is_admin_frozen_and_not_admin(request, userRequest):
            return HttpResponseRedirect(reverse('pyha:root'))
        if(int(request.POST.get('information')) == 2):
            if not target_valid(target, requestId):
                return HttpResponseRedirect(reverse('pyha:root'))
            newChatEntry = RequestInformationChatEntry()
            newChatEntry.request = userRequest
            newChatEntry.date = datetime.now()
            newChatEntry.user = request.session["user_id"]
            newChatEntry.question = False
            newChatEntry.target = target
            newChatEntry.message = request.POST.get('reason')
            newChatEntry.changedBy = changed_by_session_user(request)
            newChatEntry.save() 
            userRequest.status = StatusEnum.WAITING
            for co in Collection.objects.filter(request = userRequest):
                try:
                    if RequestInformationChatEntry.requestInformationChat.filter(request=userRequest, target=co.address).latest('date').question: 
                        userRequest.status = StatusEnum.WAITING_FOR_INFORMATION
                        break
                except RequestInformationChatEntry.DoesNotExist:
                    pass
            try:
                if RequestInformationChatEntry.requestInformationChat.filter(request=userRequest, target="sens").latest('date').question:
                    userRequest.status = StatusEnum.WAITING_FOR_INFORMATION           
            except RequestInformationChatEntry.DoesNotExist:
                pass
            try:
                if RequestInformationChatEntry.requestInformationChat.filter(request=userRequest, target="admin").latest('date').question:
                    userRequest.status = StatusEnum.WAITING_FOR_INFORMATION           
            except RequestInformationChatEntry.DoesNotExist:
                pass
            userRequest.changedBy = changed_by_session_user(request)
            userRequest.save()
            update_request_status(userRequest, userRequest.lang)
    return HttpResponseRedirect(nexturl)