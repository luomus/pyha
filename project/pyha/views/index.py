from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pyha.database import handler_mul_req_waiting_for_me_status, handler_mul_information_chat_answered_status, get_mul_all_secured, handlers_cannot_be_updated, is_downloadable, remove_request, get_last_information_chat_entry, get_collection_status_counts, withdraw_request
from pyha.localization import check_language
from pyha.login import logged_in, _process_auth_response, is_request_owner, is_admin
from pyha.models import Request, Collection, RequestLogEntry, StatusEnum
from pyha.roles import ADMIN, USER, HANDLER_ANY, CAT_HANDLER_COLL
from pyha.warehouse import fetch_email_address, get_collections_where_download_handler
from operator import attrgetter
from itertools import chain


@csrf_exempt
def pyha(http_request):
    return HttpResponseRedirect(reverse("pyha:root"))

@csrf_exempt
def index(http_request):
    if handlers_cannot_be_updated():
        return HttpResponse(status=503)
    if check_language(http_request):
        return HttpResponseRedirect(http_request.get_full_path())
    if not logged_in(http_request):
        return _process_auth_response(http_request,'')
    userId = http_request.session["user_id"]
    toast = None
    if(http_request.session.get("toast", None) is not None):
        toast = http_request.session["toast"]
        http_request.session["toast"] = None
        http_request.session.save()

    request_list = _get_request_list(http_request, userId)
    for r in request_list:
        if(r.status == StatusEnum.DOWNLOADABLE):
            r.downloadable = is_downloadable(http_request, r)

    current_roles = http_request.session.get("current_user_role", [None])
    if ADMIN in current_roles or HANDLER_ANY in current_roles:
        get_mul_all_secured(request_list, http_request)
        for r in request_list:
            r.email = fetch_email_address(r.user)
            _set_handler_statuses(http_request, r)

    if HANDLER_ANY in current_roles:
        handler_mul_information_chat_answered_status(request_list, http_request, userId)
        handler_mul_req_waiting_for_me_status(request_list, http_request, userId)
        viewedlist = list(RequestLogEntry.requestLog.filter(request__in = [re.id for re in request_list], user = userId, action = 'VIEW'))
        for r in request_list:
            if([re.request.id for re in viewedlist].count(r.id) > 0 or not r.status == StatusEnum.WAITING):
                r.viewed = True

    context = {"role": http_request.session.get("current_user_role", USER), "toast": toast, "username": http_request.session["user_name"], "requests": request_list, "static": settings.STA_URL }
    return render(http_request, 'pyha/base/index.html', context)

def group_delete_request(http_request):
    nexturl = http_request.POST.get('next', '/')
    if http_request.method == 'POST':
        if not logged_in(http_request):
            return _process_auth_response(http_request, 'pyha')
        user_id = http_request.session['user_id']
        request_id_list = [reqid.replace('request_id_','') for reqid, _ in http_request.POST.items() if 'request_id_' in reqid]
        if is_admin(http_request):
            requests = Request.objects.filter(id__in=request_id_list)
        else:
            requests = Request.objects.filter(id__in=request_id_list, user=user_id)

        for request in requests:
            if not is_admin(http_request) and request.status != 0:
                if request.status > 0:
                    withdraw_request(request, http_request)
                    RequestLogEntry.requestLog.create(request=request, user=http_request.session["user_id"], role=USER, action=RequestLogEntry.WITHDRAW)
            else:
                remove_request(request, http_request)

    return HttpResponseRedirect(nexturl)

def _get_request_list(http_request, userId):
    if ADMIN in http_request.session.get("current_user_role", [None]):
        return Request.objects.exclude(status__in=[-1, 0]).order_by('-date')
    elif HANDLER_ANY in http_request.session.get("current_user_role", [None]):
        request_list = []
        if CAT_HANDLER_COLL in http_request.session.get("user_roles", [None]):
            q = Request.objects.exclude(status__in=[-1, 0])
            request_list = q.filter(id__in=Collection.objects.filter(address__in = get_collections_where_download_handler(userId), status__gt = 0).values("request"))
        return sorted(request_list ,key=attrgetter('date'), reverse=True)
    else:
        return Request.objects.filter(user=userId).exclude(status__in=[-1]).order_by('-date')

def _set_handler_statuses(http_request, r):
    last_entry = get_last_information_chat_entry(http_request, r)
    if last_entry is None:
        r.information_status = -1
    elif last_entry.question:
        r.information_status = 0
    else:
        r.information_status = 1

    if r.status == StatusEnum.WITHDRAWN:
        r.decision_status = -1
    else:
        accepted, declined, pending = get_collection_status_counts(r.id)
        if pending == 0:
            r.decision_status = 2
        elif accepted > 0 or declined > 0:
            r.decision_status = 1
        else:
            r.decision_status = 0

    if r.downloaded is not None:
        if r.downloaded is False:
            r.download_status = 0
        elif r.decision_status == 1:
            r.download_status = 1
        else:
            r.download_status = 2
