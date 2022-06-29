from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.conf import settings
from pyha.database import create_request_view_context, check_all_collections_removed, is_downloadable
from pyha.localization import check_language
from pyha.login import logged_in, is_allowed_to_view, is_request_owner, is_admin_frozen
from pyha.models import Request, Collection, StatusEnum
from pyha.log_utils import changed_by_session_user
import requests
from http import HTTPStatus


def download_link(http_request):
    if http_request.method == 'POST':
        if not logged_in(http_request):
            return HttpResponse(status=HTTPStatus.UNAUTHORIZED)
        requestId = http_request.POST.get('requestid')
        if not is_request_owner(http_request, requestId):
            return HttpResponse(status=HTTPStatus.FORBIDDEN)
        userRequest = Request.objects.get(id=requestId)
        if is_admin_frozen(http_request, userRequest):
            return HttpResponse(status=HTTPStatus.LOCKED)
        if not (userRequest.status == 8 and is_downloadable(http_request, userRequest)):
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)

        userRequest.downloaded = True
        userRequest.changedBy = changed_by_session_user(http_request)
        userRequest.save()

        file_type = http_request.POST.get('fileType', '?')
        format = http_request.POST.get('format', '?')
        geometry = http_request.POST.get('geometry', '?')
        CRS = http_request.POST.get('CRS', '?')
        laji_id = userRequest.lajiId
        person_token = http_request.session['token']

        if file_type == 'GIS':
            url = '{}{}/{}/{}/{}?personToken={}'.format(
                settings.GEO_CONVERT_URL, laji_id.split('.')[-1], format, geometry, CRS, person_token
            )
            download_id = requests.get(url, allow_redirects=False).json()
            return HttpResponseRedirect(reverse('pyha:gis_download_status', args=(download_id,)))
        else:
            link = '{}{}?personToken={}'.format(settings.LAJIDOW_URL, laji_id, person_token)
            return JsonResponse({'status': 'complete', 'downloadUrl': link})

    return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def gis_download_status(http_request, download_id):
    if http_request.method == 'GET':
        url = '{}status/{}?timeout={}'.format(settings.GEO_CONVERT_URL, download_id, 1)
        r = requests.get(url, allow_redirects=False)

        if not r.ok:
            status_code = HTTPStatus.BAD_GATEWAY
            err_name = None
            err_msg = None

            if r.status_code == HTTPStatus.BAD_REQUEST or r.status_code == HTTPStatus.NOT_FOUND:
                status_code = r.status_code

            error = r.json()
            if 'err_name' in error:
                err_name = error['err_name']
            if 'err_msg' in error:
                err_msg = error['err_msg']

            return JsonResponse({'errName': err_name, 'errMsg': err_msg}, status=status_code)

        status_obj = r.json()
        status = status_obj['status']
        response = {
            'status': status,
            'progressPercent': status_obj['progress_percent'],
            'statusUrl': reverse('pyha:gis_download_status', args=(download_id,)),
            'downloadUrl': '{}{}'.format(settings.GEO_CONVERT_URL, r.headers['Location'].lstrip('/')) if (
                status == 'complete'
            ) else None
        }

        return JsonResponse(response)

    return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def get_api_key(http_request):
    if http_request.method == 'POST':
        if not logged_in(http_request):
            return HttpResponse(status=HTTPStatus.UNAUTHORIZED)
        requestId = http_request.POST.get('requestid')
        if not is_request_owner(http_request, requestId):
            return HttpResponse(status=HTTPStatus.FORBIDDEN)
        userRequest = Request.objects.get(id=requestId)
        if is_admin_frozen(http_request, userRequest):
            return HttpResponse(status=HTTPStatus.LOCKED)
        if not (userRequest.status == 8 and is_downloadable(http_request, userRequest)):
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)

        userRequest.downloaded = True
        userRequest.changedBy = changed_by_session_user(http_request)
        userRequest.save()

        laji_id = userRequest.lajiId
        person_token = http_request.session['token']

        response = requests.get('{}warehouse/api-keys/{}'.format(settings.LAJIAPI_URL, laji_id),
                                params={'person_token': person_token, 'access_token': settings.LAJIAPI_TOKEN},
                                timeout=settings.SECRET_TIMEOUT_PERIOD
                                )
        if not response.ok:
            return HttpResponse(status=HTTPStatus.BAD_GATEWAY)

        api_key = response.json()
        if not ('found' in api_key and api_key['found']):
            return HttpResponse(status=HTTPStatus.NOT_FOUND)

        return JsonResponse(api_key)

    return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)


def get_description_ajax(http_request):
    if http_request.method == 'POST' and http_request.POST.get('requestid'):
        if check_language(http_request):
            return HttpResponse(reverse(http_request.get_full_path()), status=310)
        if not logged_in(http_request):
            return HttpResponse(reverse('pyha:root'), status=310)
        requestId = http_request.POST.get('requestid')
        if not is_allowed_to_view(http_request, requestId):
            return HttpResponse(reverse('pyha:root'), status=310)
        userRequest = Request.objects.get(id=requestId)
        context = create_request_view_context(requestId, http_request, userRequest)
        return render(http_request, 'pyha/base/ajax/requestheader.html', context)
    return HttpResponse(reverse('pyha:root'), status=310)


def set_description_ajax(http_request):
    if http_request.method == 'POST':
        if not logged_in(http_request):
            return HttpResponse(reverse('pyha:root'), status=310)
        requestId = http_request.POST.get('requestid')
        if not is_request_owner(http_request, requestId):
            return HttpResponse(reverse('pyha:root'), status=310)
        userRequest = Request.objects.get(id=requestId)
        if is_admin_frozen(http_request, userRequest):
            return HttpResponse(reverse('pyha:root'), status=310)
        userRequest.description = http_request.POST.get('description')
        userRequest.changedBy = changed_by_session_user(http_request)
        userRequest.save()
        return HttpResponse(status=200)
    return HttpResponse(reverse('pyha:root'), status=310)


def get_collection_ajax(http_request):
    if http_request.method == 'POST' and http_request.POST.get('requestid'):
        if check_language(http_request):
            return HttpResponse(reverse(http_request.get_full_path()), status=310)
        if not logged_in(http_request):
            return HttpResponse(reverse('pyha:root'), status=310)
        requestId = http_request.POST.get('requestid')
        if not is_allowed_to_view(http_request, requestId):
            return HttpResponse(reverse('pyha:root'), status=310)
        userRequest = Request.objects.get(id=requestId)
        if is_admin_frozen(http_request, userRequest):
            return HttpResponse(reverse('pyha:root'), status=310)
        if(userRequest.status == StatusEnum.APPROVETERMS_WAIT):
            context = create_request_view_context(requestId, http_request, userRequest)
            return render(http_request, 'pyha/requestform/ajax/requestformcollection.html', context)
    return HttpResponse(reverse('pyha:root'), status=310)


def get_summary_ajax(http_request):
    if http_request.method == 'POST' and http_request.POST.get('requestid'):
        if check_language(http_request):
            return HttpResponse(reverse(http_request.get_full_path()), status=310)
        if not logged_in(http_request):
            return HttpResponse(reverse('pyha:root'), status=310)
        requestId = http_request.POST.get('requestid')
        if not is_allowed_to_view(http_request, requestId):
            return HttpResponse(reverse('pyha:root'), status=310)
        userRequest = Request.objects.get(id=requestId)
        if is_admin_frozen(http_request, userRequest):
            return HttpResponse(reverse('pyha:root'), status=310)
        if(userRequest.status == StatusEnum.APPROVETERMS_WAIT):
            context = create_request_view_context(requestId, http_request, userRequest)
            return render(http_request, 'pyha/requestform/ajax/requestformsummary.html', context)
    return HttpResponse(reverse('pyha:root'), status=310)


def create_contact_ajax(http_request):
    if http_request.method == 'POST' and http_request.POST.get('requestid') and http_request.POST.get('id'):
        if check_language(http_request):
            return HttpResponse(reverse(http_request.get_full_path()), status=310)
        if not logged_in(http_request):
            return HttpResponse(reverse('pyha:root'), status=310)
        requestId = http_request.POST.get('requestid')
        if not is_request_owner(http_request, requestId):
            return HttpResponse(reverse('pyha:root'), status=310)
        userRequest = Request.objects.get(id=requestId)
        if is_admin_frozen(http_request, userRequest):
            return HttpResponse(reverse('pyha:root'), status=310)
        if(userRequest.status == StatusEnum.APPROVETERMS_WAIT):
            context = create_request_view_context(requestId, http_request, userRequest)
            context["contact_id"] = http_request.POST.get('id')
            return render(http_request, 'pyha/requestform/ajax/requestformcontact.xml', context)
    return HttpResponse(reverse('pyha:root'), status=310)


def remove_collection_ajax(http_request):
    if http_request.method == 'POST' and http_request.POST.get('requestid'):
        if check_language(http_request):
            return HttpResponse(reverse(http_request.get_full_path()), status=310)
        if not logged_in(http_request):
            return HttpResponse(reverse('pyha:root'), status=310)
        requestId = http_request.POST.get('requestid')
        if not is_request_owner(http_request, requestId):
            return HttpResponse(reverse('pyha:root'), status=310)
        userRequest = Request.objects.get(id=requestId)
        if is_admin_frozen(http_request, userRequest):
            return HttpResponse(reverse('pyha:root'), status=310)
        collectionId = http_request.POST.get('collectionId')
        collection = Collection.objects.get(id=collectionId)
        if(userRequest.status == StatusEnum.APPROVETERMS_WAIT and collection.status != -1):
            collection.status = -1
            collection.changedBy = changed_by_session_user(http_request)
            collection.save()
            if(check_all_collections_removed(requestId)):
                return HttpResponse(reverse('pyha:root'), status=310)
            return HttpResponse(status=200)
    return HttpResponse(reverse('pyha:root'), status=310)
