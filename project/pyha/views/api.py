from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from requests.auth import HTTPBasicAuth
import requests
from pyha.email import send_mail_after_receiving_request, send_mail_after_receiving_download
from pyha.models import Request, RequestLogEntry
from pyha.roles import CAT_HANDLER_COLL
from pyha.database import count_unhandled_requests
from pyha.warehouse import store, fetch_pdf
from pyha.login import basic_auth_required
from pyha.log_utils import changed_by


@csrf_exempt
@basic_auth_required
def receiver(http_request):
    if 'JSON' in http_request.POST:
        text = http_request.POST['JSON']
        jsond = text
        userRequest = store(jsond)
    else:
        jsond = http_request.body.decode("utf-8")
        userRequest = store(jsond)
    if(userRequest):
        RequestLogEntry.requestLog.create(request=userRequest, user="Laji.fi ICT-team",
                                          role=CAT_HANDLER_COLL, action=RequestLogEntry.RECEIVE)
        send_mail_after_receiving_request(userRequest.id, userRequest.lang)
    return HttpResponse('')


@csrf_exempt
@basic_auth_required
def download(http_request, link):
    if http_request.method == 'POST':
        userRequest = get_object_or_404(Request, lajiId=link)
        if(userRequest.status == 7 and userRequest != None):
            userRequest.status = 8
            userRequest.downloadDate = datetime.now()
            userRequest.changedBy = changed_by("pyha")
            userRequest.save()
            send_mail_after_receiving_download(userRequest.id, userRequest.lang)
    return HttpResponse('')


@csrf_exempt
@basic_auth_required
def new_count(http_request):
    if http_request.method == 'GET':
        if 'none' != http_request.GET.get('person', 'none'):
            userId = http_request.GET.get('person')
            return JsonResponse({'count': count_unhandled_requests(userId)})
    return HttpResponse('')


def new_pdf(http_request):
    if http_request.method == 'POST':
        pdf_response = fetch_pdf(http_request.POST.get('source'), http_request.POST.get('style'))
        if pdf_response:
            response = HttpResponse(pdf_response, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=pyha.pdf'
            return response
        else:
            return HttpResponse(status=504)
    return HttpResponse('')


@csrf_exempt
def status(http_request):
    if http_request.method == 'GET':
        try:
            response = requests.get(settings.LAJIAPI_URL+"collections?access_token=" +
                                    settings.LAJIAPI_TOKEN, timeout=settings.SECRET_TIMEOUT_PERIOD)
            if not response.status_code == 200:
                return HttpResponse(status=504)
            response = requests.get(settings.LAJIPERSONAPI_URL+"search?objectresource=pyharesponsestatustestping", auth=HTTPBasicAuth(
                settings.LAJIPERSONAPI_USER, settings.LAJIPERSONAPI_PW), timeout=settings.SECRET_TIMEOUT_PERIOD)
            if not response.status_code == 200:
                return HttpResponse(status=504)
            response = requests.get(settings.LAJIFILTERS_URL, timeout=settings.SECRET_TIMEOUT_PERIOD)
            if not response.status_code == 200:
                return HttpResponse(status=504)
        except:
            return HttpResponse(status=504)
        return HttpResponse(status=200)
    return HttpResponse(status=405)
