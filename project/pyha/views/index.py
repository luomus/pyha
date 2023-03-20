from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext
from pyha.database import handlers_cannot_be_updated, is_downloadable, remove_request, \
    add_last_chat_entry_status_to_request_list, add_collection_counts_to_request_list, withdraw_request
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
        request_list = _add_additional_info_to_requests(http_request, request_list)

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
                data_entry['informationStatusText'] = _get_information_status_text(r)
                data_entry['downloadStatusText'] = _get_download_status_text(r)

                if ADMIN in current_roles:
                    data_entry['decisionStatusText'] = _get_decision_status_text(r)
                else:
                    data_entry['decisionStatusText'] = _get_decision_status_text_for_handler(r)
                    data_entry['waitingForUser'] = r.waiting_for_user_count > 0
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


def _add_additional_info_to_requests(http_request, request_list):
    user_id = http_request.session['user_id']
    current_roles = http_request.session.get("current_user_role", [None])

    if ADMIN in current_roles or HANDLER_ANY in current_roles:
        user_collections = None
        if HANDLER_ANY in current_roles:
            user_collections = get_collections_where_download_handler(user_id)
        request_list = add_collection_counts_to_request_list(request_list, user_collections)
        request_list = add_last_chat_entry_status_to_request_list(request_list)

    for r in request_list:
        if r.status == StatusEnum.DOWNLOADABLE:
            r.downloadable = is_downloadable(http_request, r)
        else:
            r.downloadable = False

    if ADMIN in current_roles or HANDLER_ANY in current_roles:
        users = []
        for r in request_list:
            if r.user not in users:
                users.append(r.user)
        emails = fetch_email_addresses(users)
        for r in request_list:
            r.email = emails[r.user]

    return request_list


def _get_request_list(http_request, user_id, only_uncompleted=False):
    current_roles = http_request.session.get('current_user_role', [None])
    roles = http_request.session.get('user_roles', [None])

    query = Request.objects

    excluded_status = [
        StatusEnum.WITHDRAWN,
        StatusEnum.DISCARDED,
        StatusEnum.PARTIALLY_APPROVED,
        StatusEnum.REJECTED,
        StatusEnum.APPROVED,
        StatusEnum.WAITING_FOR_DOWNLOAD,
        StatusEnum.DOWNLOADABLE
    ] if only_uncompleted else [StatusEnum.DISCARDED]

    if ADMIN in current_roles or HANDLER_ANY in current_roles:
        excluded_status.append(StatusEnum.APPROVETERMS_WAIT)
    else:
        query = query.filter(user=user_id)

    query = query.exclude(status__in=excluded_status)

    if only_uncompleted:
        query = query.exclude(frozen=True)

    if HANDLER_ANY in current_roles and CAT_HANDLER_COLL in roles:
        collections = Collection.objects.filter(address__in=get_collections_where_download_handler(user_id))
        if only_uncompleted:
            collections = collections.filter(status=Col_StatusEnum.WAITING)
        else:
            collections = collections.filter(status__gt=Col_StatusEnum.APPROVETERMS_WAIT)
        query = query.filter(collections__in=collections)

    return query


def _get_information_status_text(r):
    if r.last_chat_entry_is_question is None:
        return ''
    elif r.last_chat_entry_is_question:
        return gettext('waiting_for_additional_information')
    else:
        return gettext('user_has_given_additional_information')


def _get_decision_status_text(r):
    if r.status == StatusEnum.WITHDRAWN:
        return gettext('withdrawn')
    else:
        if r.waiting_count == 0:
            return gettext('decisions_done')
        elif r.handled_count > 0:
            return gettext('decisions_partly_done')
        else:
            return gettext('no_decisions')


def _get_decision_status_text_for_handler(r):
    if r.status == StatusEnum.WITHDRAWN:
        return gettext('withdrawn')
    else:
        if r.waiting_count == 0:
            return gettext('decisions_done')
        elif r.waiting_for_user_count == 0:
            return gettext('handler_waiting_for_others')
        else:
            return gettext('handler_waiting_for_you')


def _get_download_status_text(r):
    if r.downloaded is None:
        return ''
    else:
        if r.downloaded is False:
            return gettext('data_is_not_downloaded')
        elif r.waiting_count != 0:
            return gettext('data_is_partly_downloaded')
        else:
            return gettext('data_is_downloaded')
