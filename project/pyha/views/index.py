from functools import reduce

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pyha.database import handler_waiting_status, handler_information_answered_status, get_all_secured
from pyha.localization import check_language
from pyha.login import logged_in, _process_auth_response
from pyha.models import Request, Collection, RequestLogEntry
from pyha.roles import HANDLER_SENS, HANDLER_ANY, HANDLER_COLL
from pyha.warehouse import fetch_email_address, handlers_cannot_be_updated, get_collections_where_download_handler
from operator import attrgetter
from itertools import chain



@csrf_exempt
def index(request):
	if handlers_cannot_be_updated():
		return HttpResponse(status=503)
	if check_language(request):
		return HttpResponseRedirect(request.get_full_path())
	if not logged_in(request):
		return _process_auth_response(request,'')
	userId = request.session["user_id"]
	hasRole = HANDLER_SENS in request.session.get("user_roles", [None]) or HANDLER_COLL in request.session.get("user_roles", [None])
	if HANDLER_ANY in request.session.get("current_user_role", [None]):
		request_list = []
		if HANDLER_SENS in request.session.get("user_roles", [None]):
			request_list += Request.requests.all().exclude(status__lte=0)
		if HANDLER_COLL in request.session.get("user_roles", [None]) and not HANDLER_SENS in request.session.get("user_roles", [None]):
			#request_list += Request.requests.exclude(status__lte=0).filter(id__in=Collection.objects.filter(customSecured__gt = 0,downloadRequestHandler__contains = str(userId),status__gt = 0 ).values("request")).order_by('-date').filter(id__in=Collection.objects.filter(downloadRequestHandler__contains = str(userId),status__gt = 0 ).values("request"),sensstatus=99).order_by('-date')
			q = Request.requests.exclude(status__lte=0)
			c0 = q.filter(id__in=Collection.objects.filter(customSecured__gt = 0, address__in = get_collections_where_download_handler(userId), status__gt = 0 ).values("request"))
			c1 = q.filter(id__in=Collection.objects.filter(address__in = get_collections_where_download_handler(userId), status__gt = 0 ).values("request"), sensstatus=99)
			request_list += chain(c0, c1)
		#removes duplicates and keeps the dateorder intact when sens and coll at the same time
		#request_list = reduce(lambda r, v: v in r[1] and r or (r[0].append(v) or r[1].add(v)) or r, request_list, ([], set()))[0]
		request_list = sorted(request_list ,key=attrgetter('date'), reverse=True)
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
		return render(request, 'pyha/index.html', context)













