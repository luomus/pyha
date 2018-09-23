from datetime import datetime

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pyha.email import send_mail_after_receiving_request, send_mail_after_receiving_download
from pyha.models import RequestLogEntry, RequestInformationChatEntry, Request, Collection
from pyha.roles import HANDLER_SENS
from pyha.warehouse import store, fetch_role, fetch_pdf
from wsgi import basic_auth_required


@csrf_exempt
@basic_auth_required
def receiver(request):
        if 'JSON' in request.POST:
            text = request.POST['JSON']
            jsond = text
            req = store(jsond)
        else:
            jsond = request.body.decode("utf-8")
            req = store(jsond)
        if(req):
            send_mail_after_receiving_request(req.id, req.lang)
        return HttpResponse('')

@csrf_exempt
@basic_auth_required
def download(request, link):
        if request.method == 'POST':
            userRequest = Request.requests.get(lajiId=link)
            userRequest.status = 8
            userRequest.downloadDate = datetime.now()
            userRequest.save()
            send_mail_after_receiving_download(userRequest.id)
        return HttpResponse('')
    
@csrf_exempt
@basic_auth_required
def new_count(request):
        if request.method == 'GET':
            if 'none' != request.GET.get('person', 'none'):
                personId = request.GET.get('person')
                role = fetch_role(personId)
                count = 0
                if(settings.TUN_URL+HANDLER_SENS in role.values()):
                    request_list = Request.requests.exclude(status__lte=0)
                    for r in request_list:
                        if(RequestLogEntry.requestLog.filter(request = r.id, user = request.GET.get('person'), action = 'VIEW').count() == 0):
                            count += 1
                        else:
                            if r.sensstatus == 1 and RequestInformationChatEntry.requestInformationChat.filter(request=r.id).count() > 0:
                                chat = RequestInformationChatEntry.requestInformationChat.filter(request=r.id).order_by('-date')[0]
                                if not chat.question:
                                    count += 1
                else:
                    request_list = Request.requests.exclude(status__lte=0).filter(id__in=Collection.objects.filter(customSecured__gt = 0,downloadRequestHandler__contains = str(personId),status__gt = 0 ).values("request"))
                    for r in request_list:
                        if(RequestLogEntry.requestLog.filter(request = r.id, user = request.GET.get('person'), action = 'VIEW').count() == 0):
                            count += 1
                return JsonResponse({'count':count})
        return HttpResponse('')

def new_pdf(request):
        if request.method == 'POST':
            response = HttpResponse(fetch_pdf(request.POST.get('source'),request.POST.get('style')),content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=pyha.pdf'
            return response
        return HttpResponse('')

def jsonmock(request):
        return render(request, 'pyha/mockjson.html')
        