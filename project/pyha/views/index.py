from functools import reduce

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pyha.database import handler_waiting_status, handler_information_answered_status, get_all_secured
from pyha.localization import check_language
from pyha.login import logged_in, _process_auth_response
from pyha.models import Request, Collection, RequestLogEntry
from pyha.roles import HANDLER_SENS, HANDLER_ANY, HANDLER_COLL
from pyha.warehouse import fetch_email_address
from pyha.email import mail_test




@csrf_exempt
def index(request):
	if check_language(request):
		return HttpResponseRedirect(request.get_full_path())
	if not logged_in(request):
		return _process_auth_response(request,'')
	userId = request.session["user_id"]
	hasRole = HANDLER_SENS in request.session.get("user_roles", [None]) or HANDLER_COLL in request.session.get("user_roles", [None])
	if HANDLER_ANY in request.session.get("current_user_role", [None]):
		request_list = []
		if HANDLER_SENS in request.session.get("user_roles", [None]):
			request_list += Request.requests.all().exclude(status__lte=0).order_by('-date')
		if HANDLER_COLL in request.session.get("user_roles", [None]):
			request_list += Request.requests.exclude(status__lte=0).filter(id__in=Collection.objects.filter(customSecured__gt = 0,downloadRequestHandler__contains = str(userId),status__gt = 0 ).values("request")).order_by('-date').filter(id__in=Collection.objects.filter(downloadRequestHandler__contains = str(userId),status__gt = 0 ).values("request"),sensstatus=99).order_by('-date')
		request_list = reduce(lambda r, v: v in r[1] and r or (r[0].append(v) or r[1].add(v)) or r, request_list, ([], set()))[0]
		for r in request_list:
			r.allSecured = get_all_secured(request, r)
			r.email = fetch_email_address(r.user)
			handler_waiting_status(r, request, userId)
			handler_information_answered_status(r, request, userId)
			if(RequestLogEntry.requestLog.filter(request = r.id, user = userId, action = 'VIEW').count() > 0):
				r.viewed = True
		context = {"role": hasRole, "username": request.session["user_name"], "requests": request_list, "static": settings.STA_URL }
		return render(request, 'pyha/handler/index.html', context)
	else:
		request_list = Request.requests.filter(user=userId, status__gte=0).order_by('-date')
		for r in request_list:
			r.allSecured = get_all_secured(request, r)
		context = {"role": hasRole, "username": request.session["user_name"], "requests": request_list, "static": settings.STA_URL }
		mail_test()
		return render(request, 'pyha/index.html', context)













