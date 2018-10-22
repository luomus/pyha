from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from pyha.email import send_mail_after_receiving_request, send_mail_after_receiving_download
from pyha.models import Request
from pyha.database import count_unhandled_requests
from pyha.warehouse import store, fetch_pdf
from pyha.login import basic_auth_required


@csrf_exempt
@basic_auth_required
def receiver(request):
        if 'JSON' in request.POST:
            text = request.POST['JSON']
            jsond = text
            userRequest = store(jsond)
        else:
            jsond = request.body.decode("utf-8")
            userRequest = store(jsond)
        if(userRequest):
            send_mail_after_receiving_request(userRequest.id, userRequest.lang)
        return HttpResponse('')

@csrf_exempt
@basic_auth_required
def download(request, link):
        if request.method == 'POST':
            userRequest = get_object_or_404(Request, lajiId=link)
            if(userRequest.status == 7 and userRequest != None):
                userRequest.status = 8
                userRequest.downloadDate = datetime.now()
                userRequest.save()
                send_mail_after_receiving_download(userRequest.id, userRequest.lang)
        return HttpResponse('')
    
@csrf_exempt
@basic_auth_required
def new_count(request):
        if request.method == 'GET':
            if 'none' != request.GET.get('person', 'none'):
                userId = request.GET.get('person')
                return JsonResponse({'count':count_unhandled_requests(userId)})
        return HttpResponse('')

def new_pdf(request):
        if request.method == 'POST':
            response = HttpResponse(fetch_pdf(request.POST.get('source'),request.POST.get('style')),content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=pyha.pdf'
            return response
        return HttpResponse('')

def jsonmock(request):
        return render(request, 'pyha/mockjson.html')
        