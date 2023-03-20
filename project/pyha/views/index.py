from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pyha.database import handler_mul_information_chat_answered_status, handlers_cannot_be_updated, is_downloadable, remove_request, add_last_chat_entry_status_to_request_list, add_collection_counts_to_request_list, withdraw_request
from pyha.localization import check_language
from pyha.login import logged_in, _process_auth_response, is_admin
from pyha.models import Request, Collection, RequestLogEntry, StatusEnum, Col_StatusEnum
from pyha.roles import ADMIN, USER, HANDLER_ANY, CAT_HANDLER_COLL
from pyha.warehouse import get_collections_where_download_handler, fetch_email_addresses
from pyha.templatetags.pyha_tags import translateRequestStatus


def csrf_failure(http_request, reason=""):
    return render(http_request, 'pyha/error/403_crsf.html', {'static': settings.STA_URL, 'version': settings.VERSION})


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
        return _process_auth_response(http_request, '')
    userId = http_request.session["user_id"]
    toast = None
    if(http_request.session.get("toast", None) is not None):
        toast = http_request.session["toast"]
        http_request.session["toast"] = None
        http_request.session.save()

    request_list = _get_request_list(http_request, userId)
    context = {
        "role": http_request.session.get("current_user_role", USER),
        "toast": toast,
        "username": http_request.session["user_name"],
        "has_requests": len(request_list) > 0,
        "static": settings.STA_URL,
        "version": settings.VERSION
    }
    return render(http_request, 'pyha/base/index.html', context)


def get_request_list_ajax(http_request):
    if http_request.method == 'GET':
        if not logged_in(http_request):
            return HttpResponse(reverse('pyha:root'), status=310)

        only_uncompleted = http_request.GET.get('onlyUncompleted', 'false') == 'true'

        user_id = http_request.session['user_id']
        current_roles = http_request.session.get('current_user_role', [None])

        request_list = _get_request_list(http_request, user_id, only_uncompleted)
        request_list = _add_additional_info_to_requests(http_request, user_id, request_list)

        data = []
        for r in request_list:
            data_entry = {
                'id': r.id,
                'status': r.status,
                'date': r.date
            }
            if ADMIN in current_roles or HANDLER_ANY in current_roles:
                data_entry['email'] = r.email
                data_entry['observationCount'] = r.observation_count
                data_entry['informationStatus'] = r.information_status
                data_entry['decisionStatus'] = r.decision_status
                data_entry['downloadStatus'] = r.download_status

                if HANDLER_ANY in current_roles:
                    data_entry['viewed'] = r.viewed
                    data_entry['answerStatus'] = r.answerstatus
            else:
                data_entry['approximateMatches'] = r.approximateMatches
                data_entry['description'] = r.description
                data_entry['statusText'] = translateRequestStatus(r.status, USER, None, None, r.downloadable)

            data.append(data_entry)

        result = {
            'data': data
        }

        return JsonResponse(result)

    return HttpResponse(reverse('pyha:root'), status=310)


def group_delete_request(http_request):
    nexturl = http_request.POST.get('next', '/')
    if http_request.method == 'POST':
        if not logged_in(http_request):
            return _process_auth_response(http_request, 'pyha')
        user_id = http_request.session['user_id']
        request_id_list = [reqid.replace('request_id_', '')
                           for reqid, _ in http_request.POST.items() if 'request_id_' in reqid]
        if is_admin(http_request):
            requests = Request.objects.filter(id__in=request_id_list)
        else:
            requests = Request.objects.filter(id__in=request_id_list, user=user_id)

        for request in requests:
            if not is_admin(http_request) and request.status != 0:
                if request.status > 0:
                    withdraw_request(request, http_request)
                    RequestLogEntry.requestLog.create(
                        request=request, user=http_request.session["user_id"], role=USER, action=RequestLogEntry.WITHDRAW)
            else:
                remove_request(request, http_request)

    return HttpResponseRedirect(nexturl)


def _add_additional_info_to_requests(http_request, userId, request_list):
    current_roles = http_request.session.get("current_user_role", [None])

    if ADMIN in current_roles or HANDLER_ANY in current_roles:
        request_list = add_collection_counts_to_request_list(request_list)
        request_list = add_last_chat_entry_status_to_request_list(request_list)

    for r in request_list:
        if r.status == StatusEnum.DOWNLOADABLE:
            r.downloadable = is_downloadable(http_request, r)
        else:
            r.downloadable = False

    if ADMIN in current_roles or HANDLER_ANY in current_roles:
        _add_handler_values(request_list)

        users = []
        for r in request_list:
            if r.user not in users:
                users.append(r.user)
        emails = fetch_email_addresses(users)
        for r in request_list:
            r.email = emails[r.user]

    if HANDLER_ANY in current_roles:
        handler_mul_information_chat_answered_status(request_list, http_request, userId)
        viewedlist = list(RequestLogEntry.requestLog.filter(
            request__in=[re.id for re in request_list], user=userId, action='VIEW'))
        for r in request_list:
            if [re.request.id for re in viewedlist].count(r.id) > 0 or not r.status == StatusEnum.WAITING:
                r.viewed = True
            else:
                r.viewed = False

    return request_list


def _get_request_list(http_request, userId, only_uncompleted=False):
    current_roles = http_request.session.get('current_user_role', [None])
    roles = http_request.session.get('user_roles', [None])

    completed_status = [
        StatusEnum.WITHDRAWN,
        StatusEnum.DISCARDED,
        StatusEnum.PARTIALLY_APPROVED,
        StatusEnum.REJECTED,
        StatusEnum.APPROVED,
        StatusEnum.WAITING_FOR_DOWNLOAD,
        StatusEnum.DOWNLOADABLE
    ]
    excluded_status = completed_status if only_uncompleted else [StatusEnum.DISCARDED]

    query = Request.objects
    if ADMIN in current_roles or HANDLER_ANY in current_roles:
        excluded_status.append(StatusEnum.APPROVETERMS_WAIT)

        if HANDLER_ANY in current_roles and CAT_HANDLER_COLL in roles:
            collections = Collection.objects.filter(address__in=get_collections_where_download_handler(userId))
            if only_uncompleted:
                collections = collections.filter(status=Col_StatusEnum.WAITING)
            else:
                collections = collections.filter(status__gt=Col_StatusEnum.APPROVETERMS_WAIT)
            query = query.filter(id__in=collections.values('request'))
    else:
        query = query.filter(user=userId)

    query = query.exclude(status__in=excluded_status)
    if only_uncompleted:
        query = query.exclude(frozen=True)

    return query


def _add_handler_values(request_list):
    for idx, r in enumerate(request_list):
        if r.last_chat_entry_is_question is None:
            r.information_status = -1
        elif r.last_chat_entry_is_question:
            r.information_status = 0
        else:
            r.information_status = 1

        if r.status == StatusEnum.WITHDRAWN:
            r.decision_status = -1
        else:
            if r.waiting_count == 0:
                r.decision_status = 2
            elif r.handled_count > 0:
                r.decision_status = 1
            else:
                r.decision_status = 0

        if r.downloaded is None:
            r.download_status = None
        else:
            if r.downloaded is False:
                r.download_status = 0
            elif r.decision_status == 1:
                r.download_status = 1
            else:
                r.download_status = 2
