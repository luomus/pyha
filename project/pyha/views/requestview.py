from datetime import datetime
import os

from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from pyha.database import create_request_view_context, make_logEntry_view, update_request_status, target_valid, contains_approved_collection, handlers_cannot_be_updated, update_collection_status, is_downloadable
from pyha.email import send_mail_after_additional_information_requested, send_mail_after_additional_information_received, send_raw_mail
from pyha.localization import check_language
from pyha.login import logged_in, _process_auth_response, is_allowed_to_view, is_request_owner, is_admin_frozen, is_allowed_to_ask_information_as_target, is_admin, is_allowed_to_handle
from pyha.models import HandlerInRequest, RequestLogEntry, RequestHandlerChatEntry, RequestInformationChatEntry, Request, Collection, StatusEnum, Col_StatusEnum, File
from pyha.roles import HANDLER_ANY, CAT_HANDLER_COLL, ADMIN, CAT_ADMIN, USER
from pyha.warehouse import send_download_request, update_collections
from pyha.log_utils import changed_by_session_user
from pyha import toast
import PyPDF2


@csrf_exempt
def show_request(http_request):
    if check_language(http_request):
        return HttpResponseRedirect(http_request.get_full_path())
    # Has Access
    requestId = os.path.basename(os.path.normpath(http_request.path))
    if handlers_cannot_be_updated():
        return HttpResponse(status=503)
    if not logged_in(http_request):
        return _process_auth_response(http_request, "request/"+requestId)
    if not is_allowed_to_view(http_request, requestId):
        return HttpResponseRedirect(reverse('pyha:root'))
    userRequest = Request.objects.get(id=requestId)
    userId = http_request.session["user_id"]
    role = http_request.session.get("current_user_role", USER)
    if (userRequest.user == userId and role != USER) or userRequest.user != userId:
        # make a log entry
        make_logEntry_view(http_request, userRequest, userId, role)
    context = create_request_view_context(requestId, http_request, userRequest)

    if userRequest.status == 0:
        return render(http_request, 'pyha/requestform/requestform.html', context)

    update_request_status(userRequest, userRequest.lang)
    return render(http_request, 'pyha/requestview/requestview.html', context)


def comment_handler(http_request):
    nexturl = http_request.POST.get('next', '/')
    if http_request.method == 'POST':
        requestId = http_request.POST.get('requestid', '?')
        target = http_request.POST.get('target', '?')
        message = http_request.POST.get('commentsForHandlers')
        if not logged_in(http_request):
            return _process_auth_response(http_request, "pyha")
        if not is_allowed_to_view(http_request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        userRequest = Request.objects.get(id=requestId)
        if is_allowed_to_ask_information_as_target(http_request, target, requestId):
            newChatEntry = RequestHandlerChatEntry()
            newChatEntry.request = userRequest
            newChatEntry.target = target
            newChatEntry.date = datetime.now()
            newChatEntry.user = http_request.session["user_id"]
            newChatEntry.message = message
            newChatEntry.changedBy = changed_by_session_user(http_request)
            newChatEntry.save()
    return HttpResponseRedirect(nexturl)


def initialize_download(http_request):
    nexturl = http_request.POST.get('next', '/')
    if http_request.method == 'POST':
        requestId = http_request.POST.get('requestid', '?')
        if not logged_in(http_request):
            return _process_auth_response(http_request, "pyha")
        if not is_allowed_to_view(http_request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        if not is_request_owner(http_request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        userRequest = Request.objects.get(id=requestId)
        if is_admin_frozen(http_request, userRequest):
            return HttpResponseRedirect(reverse('pyha:root'))
        if(not userRequest.frozen or ADMIN in http_request.session["current_user_role"]):
            if (userRequest.status == 4 or userRequest.status == 2 or contains_approved_collection(requestId)):
                send_download_request(requestId)
                userRequest.status = 7
                userRequest.changedBy = changed_by_session_user(http_request)
                userRequest.save()
    return HttpResponseRedirect(nexturl)


def change_description(http_request):
    if http_request.method == 'POST':
        nexturl = http_request.POST.get('next', '/')
        requestId = http_request.POST.get('requestid')
        if not logged_in(http_request):
            return _process_auth_response(http_request, "pyha")
        if not is_request_owner(http_request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        userRequest = Request.objects.get(id=requestId)
        if is_admin_frozen(http_request, userRequest):
            return HttpResponseRedirect(reverse('pyha:root'))
        userRequest.description = http_request.POST.get('description')
        userRequest.changedBy = changed_by_session_user(http_request)
        userRequest.save()
        return HttpResponseRedirect(nexturl)
    return HttpResponseRedirect(reverse('pyha:root'))


def freeze(http_request):
    if http_request.method == 'POST':
        nexturl = http_request.POST.get('next', '/')
        requestId = http_request.POST.get('requestid')
        if not logged_in(http_request):
            return _process_auth_response(http_request, "pyha")
        if not is_admin(http_request):
            return HttpResponse(status=404)
        userRequest = Request.objects.get(id=requestId)
        if userRequest.frozen:
            userRequest.frozen = False
        else:
            userRequest.frozen = True
        userRequest.changedBy = changed_by_session_user(http_request)
        userRequest.save()
        return HttpResponseRedirect(nexturl)
    return HttpResponse(status=404)


def refresh_collections_cache(http_request):
    if http_request.method == 'POST':
        nexturl = http_request.POST.get('next', '/')
        if not logged_in(http_request):
            return _process_auth_response(http_request, "pyha")
        if not is_admin(http_request):
            return HttpResponse(status=404)
        update_collections()
        return HttpResponseRedirect(nexturl)
    return HttpResponse(status=404)


def send_email(http_request):
    if http_request.method == 'POST':
        nexturl = http_request.POST.get('next', '/')
        requestId = http_request.POST.get('requestid')
        if not logged_in(http_request):
            return _process_auth_response(http_request, "pyha")
        if not is_admin(http_request):
            return HttpResponse(status=404)
        id_list = [{'id': userid.replace('email_id_', ''), 'email': email}
                   for userid, email in http_request.POST.items() if 'email_id_' in userid]
        sender = http_request.POST.get('com_email_sender')
        recipients = [userid['email'] for userid in id_list]
        subject = http_request.POST.get('com_email_header')
        content = http_request.POST.get('com_email_content').replace(u'\ufeff', '')
        handlers = HandlerInRequest.objects.filter(request=requestId)
        ids = [userid['id'] for userid in id_list]
        for userid in ids:
            found_in_db = False
            for handler in handlers:
                if userid in handler.user:
                    found_in_db = True
                    handler.request = Request.objects.get(id=requestId)
                    handler.emailed = True
                    handler.changedBy = changed_by_session_user(http_request)
                    handler.save()
                    break
            if not found_in_db:
                handler = HandlerInRequest()
                handler.user = userid
                handler.request = Request.objects.get(id=requestId)
                handler.emailed = True
                handler.changedBy = changed_by_session_user(http_request)
                handler.save()
        for recipient in recipients:
            send_raw_mail(subject, sender, [recipient], content)
        http_request.session["toast"] = {"status": toast.POSITIVE, "message": ugettext('toast_mails_sent_succesfully')}
        return HttpResponseRedirect(nexturl)
    return HttpResponse(status=404)


def answer(http_request):
    nexturl = http_request.POST.get('next', '/')
    if http_request.method == 'POST':
        if not logged_in(http_request):
            return _process_auth_response(http_request, "pyha")
        requestId = http_request.POST.get('requestid', '?')
        target = http_request.POST.get('target', '?')
        if not is_allowed_to_handle(http_request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        collectionId = http_request.POST.get('collectionid')
        userRequest = Request.objects.get(id=requestId)
        if is_admin_frozen(http_request, userRequest):
            return HttpResponseRedirect(reverse('pyha:root'))
        if userRequest.status == StatusEnum.WAITING_FOR_DOWNLOAD or userRequest.status == StatusEnum.DOWNLOADABLE:
            return HttpResponseRedirect(reverse('pyha:root'))
        collection = Collection.objects.get(request=requestId, address=collectionId)
        update_collection_status(http_request, userRequest, collection)
    return HttpResponseRedirect(nexturl)


def group_answer(http_request):
    nexturl = http_request.POST.get('next', '/')
    if http_request.method == 'POST':
        if not logged_in(http_request):
            return _process_auth_response(http_request, "pyha")
        requestId = http_request.POST.get('requestid', '?')
        if not is_allowed_to_handle(http_request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        userRequest = Request.objects.get(id=requestId)
        if is_admin_frozen(http_request, userRequest):
            return HttpResponseRedirect(reverse('pyha:root'))
        if userRequest.status == StatusEnum.WAITING_FOR_DOWNLOAD or userRequest.status == StatusEnum.DOWNLOADABLE:
            return HttpResponseRedirect(reverse('pyha:root'))
        id_list = [{'id': colid.replace('collection_id_', ''), 'address': address}
                   for colid, address in http_request.POST.items() if 'collection_id_' in colid]
        collections = Collection.objects.filter(request=requestId, id__in=[ide['id'] for ide in id_list], address__in=[
                                                ide['address'] for ide in id_list])
        for collection in collections:
            update_collection_status(http_request, userRequest, collection)
    return HttpResponseRedirect(nexturl)


def question(http_request):
    nexturl = http_request.POST.get('next', '/')
    if http_request.method == 'POST':
        if not logged_in(http_request):
            return _process_auth_response(http_request, "pyha")
        requestId = http_request.POST.get('requestid', '?')
        target = http_request.POST.get('target', '?')
        if not is_allowed_to_handle(http_request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        userRequest = Request.objects.get(id=requestId)
        if(int(http_request.POST.get('answer')) == 2):
            if not is_allowed_to_ask_information_as_target(http_request, target, requestId):
                return HttpResponseRedirect(reverse('pyha:root'))
            newChatEntry = RequestInformationChatEntry()
            newChatEntry.request = Request.objects.get(id=requestId)
            newChatEntry.date = datetime.now()
            newChatEntry.user = http_request.session["user_id"]
            newChatEntry.question = True
            newChatEntry.target = target
            newChatEntry.message = http_request.POST.get('reason')

            response = _add_file_to_chat_entry(http_request, newChatEntry, nexturl)
            if response is not None:
                return response

            newChatEntry.changedBy = changed_by_session_user(http_request)
            newChatEntry.save()
            userRequest.status = StatusEnum.WAITING_FOR_INFORMATION
            userRequest.changedBy = changed_by_session_user(http_request)
            userRequest.save()
            send_mail_after_additional_information_requested(requestId, userRequest.lang)
    return HttpResponseRedirect(nexturl)


def information(http_request):
    nexturl = http_request.POST.get('next', '/')
    if http_request.method == 'POST':
        if not logged_in(http_request):
            return _process_auth_response(http_request, "pyha")
        requestId = http_request.POST.get('requestid', '?')
        target = http_request.POST.get('target', '?')
        if not is_allowed_to_view(http_request, requestId):
            return HttpResponseRedirect(reverse('pyha:root'))
        userRequest = Request.objects.get(id=requestId)
        if(int(http_request.POST.get('information')) == 2):
            if not target_valid(target, requestId):
                return HttpResponseRedirect(reverse('pyha:root'))
            newChatEntry = RequestInformationChatEntry()
            newChatEntry.request = userRequest
            newChatEntry.date = datetime.now()
            newChatEntry.user = http_request.session["user_id"]
            newChatEntry.question = False
            newChatEntry.target = target
            newChatEntry.message = http_request.POST.get('reason')

            response = _add_file_to_chat_entry(http_request, newChatEntry, nexturl)
            if response is not None:
                return response

            newChatEntry.changedBy = changed_by_session_user(http_request)
            newChatEntry.save()
            userRequest.status = StatusEnum.WAITING
            for co in Collection.objects.filter(request=userRequest):
                try:
                    if RequestInformationChatEntry.requestInformationChat.filter(request=userRequest, target=co.address).latest('date').question:
                        userRequest.status = StatusEnum.WAITING_FOR_INFORMATION
                        break
                except RequestInformationChatEntry.DoesNotExist:
                    pass
            try:
                if RequestInformationChatEntry.requestInformationChat.filter(request=userRequest, target="admin").latest('date').question:
                    userRequest.status = StatusEnum.WAITING_FOR_INFORMATION
            except RequestInformationChatEntry.DoesNotExist:
                pass
            userRequest.changedBy = changed_by_session_user(http_request)
            userRequest.save()
            update_request_status(userRequest, userRequest.lang)
            users = RequestInformationChatEntry.requestInformationChat.filter(
                request=userRequest, question=True).values_list('user', flat=True).distinct()
            send_mail_after_additional_information_received(requestId, users)
    return HttpResponseRedirect(nexturl)


def chat_entry_file_download(http_request):
    if http_request.method == 'POST':
        if not logged_in(http_request):
            return _process_auth_response(http_request, 'pyha')

        chat_entry_id = http_request.POST.get('chatEntryId', '?')
        chat_entry = RequestInformationChatEntry.requestInformationChat.get(id=chat_entry_id)
        request_id = chat_entry.request.id

        if not is_allowed_to_view(http_request, request_id):
            return HttpResponseRedirect(reverse('pyha:root'))
        if not (
            is_request_owner(http_request, request_id) or
            is_allowed_to_ask_information_as_target(http_request, chat_entry.target, request_id)
        ):
            return HttpResponseRedirect(reverse('pyha:root'))

        file = chat_entry.file
        response = HttpResponse(file.content)
        response['Content-Type'] = file.contentType
        response['Content-Disposition'] = 'attachment;filename={}'.format(file.fileName)
        return response
    return HttpResponseRedirect(reverse('pyha:root'))


def _add_file_to_chat_entry(http_request, new_chat_entry, nexturl):
    if 'reasonFile' in http_request.FILES:
        attached_file = http_request.FILES['reasonFile']
        if attached_file.size > settings.MAX_UPLOAD_FILE_SIZE or not attached_file.name.endswith('.pdf'):
            http_request.session["toast"] = {
                "status": toast.ERROR,
                "message": ugettext('file_upload_failed')
            }
            http_request.session.save()
            return HttpResponseRedirect(nexturl)
        try:
            PyPDF2.PdfFileReader(attached_file)
        except PyPDF2.utils.PdfReadError:
            http_request.session["toast"] = {
                "status": toast.ERROR,
                "message": ugettext('file_upload_failed')
            }
            http_request.session.save()
            return HttpResponseRedirect(nexturl)

        attached_file.seek(0)
        file = File(
            content=attached_file.read(),
            fileName=attached_file.name,
            contentType='application/pdf'
        )
        file.save()
        new_chat_entry.file = file
