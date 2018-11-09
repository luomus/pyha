from functools import reduce

from django.utils.translation import ugettext
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pyha.database import handler_waiting_status, handler_information_answered_status, get_all_secured, handlers_cannot_be_updated
from pyha.localization import check_language
from pyha.login import logged_in, _process_auth_response
from pyha.models import Request, Collection, RequestLogEntry, StatusEnum, Sens_StatusEnum
from pyha.roles import ADMIN, CAT_HANDLER_SENS, HANDLER_ANY, CAT_HANDLER_COLL
from pyha.warehouse import fetch_email_address, get_collections_where_download_handler
from operator import attrgetter
from itertools import chain


@csrf_exempt
def pyha(request):
	return HttpResponseRedirect(reverse("pyha:root"))

@csrf_exempt
def index(request):
	if handlers_cannot_be_updated():
		return HttpResponse(status=503)
	if check_language(request):
		return HttpResponseRedirect(request.get_full_path())
	if not logged_in(request):
		return _process_auth_response(request,'')
	userId = request.session["user_id"]
	hasRole = CAT_HANDLER_SENS in request.session.get("user_roles", [None]) or CAT_HANDLER_COLL in request.session.get("user_roles", [None]) or ADMIN in request.session.get("user_roles", [None]) 
	if ADMIN in request.session.get("current_user_role", [None]):
		request_list = Request.objects.filter(status__gt=0)
		for r in request_list:
			r.allSecured = get_all_secured(r)
			r.email = fetch_email_address(r.user)
		context = {"role": hasRole, "message": request.session.get("message", None), "username": request.session["user_name"], "requests": request_list, "static": settings.STA_URL }
		if(request.session.get("message", None) is not None):
			request.session["message"] = None
			request.session.save()
		return render(request, 'pyha/base/admin/index.html', context)
	elif HANDLER_ANY in request.session.get("current_user_role", [None]):
		request_list = []
		if CAT_HANDLER_SENS in request.session.get("user_roles", [None]):
			q = Request.objects.exclude(status__lte=0)
			request_list += q.filter(id__in=Collection.objects.filter(taxonSecured__gt = 0, status__gt = 0).values("request")).exclude(sensstatus=Sens_StatusEnum.IGNORE_OFFICIAL)
		if CAT_HANDLER_COLL in request.session.get("user_roles", [None]) and not CAT_HANDLER_SENS in request.session.get("user_roles", [None]):
			#request_list += Request.objects.exclude(status__lte=0).filter(id__in=Collection.objects.filter(customSecured__gt = 0,downloadRequestHandler__contains = str(userId),status__gt = 0 ).values("request")).order_by('-date').filter(id__in=Collection.objects.filter(downloadRequestHandler__contains = str(userId),status__gt = 0 ).values("request"),sensstatus=99).order_by('-date')
			q = Request.objects.exclude(status__lte=0)
			c0 = q.filter(id__in=Collection.objects.filter(customSecured__gt = 0, address__in = get_collections_where_download_handler(userId), status__gt = 0).values("request")).exclude(sensstatus=Sens_StatusEnum.IGNORE_OFFICIAL)
			c1 = q.filter(id__in=Collection.objects.filter(address__in = get_collections_where_download_handler(userId), status__gt = 0 ).values("request"), sensstatus=Sens_StatusEnum.IGNORE_OFFICIAL)
			request_list = chain(c0, c1, request_list)
		#sort by date
		request_list = sorted(request_list ,key=attrgetter('date'), reverse=True)
		for r in request_list:
			r.allSecured = get_all_secured(r)
			r.email = fetch_email_address(r.user)
			handler_waiting_status(r, request, userId)
			handler_information_answered_status(r, request, userId)
			if(RequestLogEntry.requestLog.filter(request = r.id, user = userId, action = 'VIEW').count() > 0 or not r.status == StatusEnum.WAITING):
				r.viewed = True
		context = {"role": hasRole, "message": request.session.get("message", None), "username": request.session["user_name"], "requests": request_list, "static": settings.STA_URL }
		if(request.session.get("message", None) is not None):
			request.session["message"] = None
			request.session.save()
		return render(request, 'pyha/base/handler/index.html', context)
	else:
		request_list = Request.objects.filter(user=userId, status__gte=0).order_by('-date')
		context = {"role": hasRole, "message": request.session.get("message", None), "username": request.session["user_name"], "requests": request_list, "static": settings.STA_URL }
		if(request.session.get("message", None) is not None): 
			request.session["message"] = None
			request.session.save()
		return render(request, 'pyha/base/index.html', context)










