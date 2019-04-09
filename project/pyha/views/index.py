from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pyha.database import handler_mul_req_waiting_for_me_status, handler_mul_information_chat_answered_status, get_mul_all_secured, handlers_cannot_be_updated, is_downloadable
from pyha.localization import check_language
from pyha.login import logged_in, _process_auth_response
from pyha.models import Request, Collection, RequestLogEntry, StatusEnum, Sens_StatusEnum
from pyha.roles import ADMIN, CAT_HANDLER_SENS, HANDLER_ANY, CAT_HANDLER_COLL, ROLES_SHOWN_ROLE_IN_HEADER
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
	hasRoleHeader = any([role in http_request.session.get("user_roles", [None]) for role in ROLES_SHOWN_ROLE_IN_HEADER])
	toast = None
	if(http_request.session.get("toast", None) is not None): 
		toast = http_request.session["toast"]
		http_request.session["toast"] = None
		http_request.session.save()
	if ADMIN in http_request.session.get("current_user_role", [None]):
		request_list = Request.objects.filter(status__gt=0)
		get_mul_all_secured(request_list)
		for r in request_list:
			if(r.status == StatusEnum.DOWNLOADABLE):
				r.downloadable = is_downloadable(http_request, r)
			r.email = fetch_email_address(r.user)
		context = {"role": hasRoleHeader, "toast": toast, "username": http_request.session["user_name"], "requests": request_list, "static": settings.STA_URL }
		return render(http_request, 'pyha/base/admin/index.html', context)
	elif HANDLER_ANY in http_request.session.get("current_user_role", [None]):
		request_list = []
		if CAT_HANDLER_SENS in http_request.session.get("user_roles", [None]):
			q = Request.objects.exclude(status__lte=0)
			request_list += q.filter(id__in=Collection.objects.filter(taxonSecured__gt = 0, status__gt = 0).values("request")).exclude(sensStatus=Sens_StatusEnum.IGNORE_OFFICIAL)
		if CAT_HANDLER_COLL in http_request.session.get("user_roles", [None]):
			q = Request.objects.exclude(status__lte=0)
			c0 = q.filter(id__in=Collection.objects.filter(customSecured__gt = 0, address__in = get_collections_where_download_handler(userId), status__gt = 0).values("request")).exclude(sensStatus=Sens_StatusEnum.IGNORE_OFFICIAL)
			c1 = q.filter(id__in=Collection.objects.filter(address__in = get_collections_where_download_handler(userId), status__gt = 0 ).values("request"), sensStatus=Sens_StatusEnum.IGNORE_OFFICIAL)
			request_list = chain(c0, c1, request_list)
		request_list = sorted(request_list ,key=attrgetter('date'), reverse=True)
		handler_mul_information_chat_answered_status(request_list, http_request, userId)
		handler_mul_req_waiting_for_me_status(request_list, http_request, userId)	
		viewedlist = list(RequestLogEntry.requestLog.filter(request__in = [re.id for re in request_list], user = userId, action = 'VIEW'))	
		get_mul_all_secured(request_list)	
		for r in request_list:
			if(r.status == StatusEnum.DOWNLOADABLE):
				r.downloadable = is_downloadable(http_request, r)
			r.email = fetch_email_address(r.user)
			if([re.request.id for re in viewedlist].count(r.id) > 0 or not r.status == StatusEnum.WAITING):
				r.viewed = True
			
		context = {"role": hasRoleHeader, "toast": toast, "username": http_request.session["user_name"], "requests": request_list, "static": settings.STA_URL }
		rend = render(http_request, 'pyha/base/handler/index.html', context)
		return rend
	else:
		request_list = Request.objects.filter(user=userId, status__gte=0).order_by('-date')
		for r in request_list:
			if(r.status == StatusEnum.DOWNLOADABLE):
				r.downloadable = is_downloadable(http_request, r)
		context = {"role": hasRoleHeader, "toast": toast, "username": http_request.session["user_name"], "requests": request_list, "static": settings.STA_URL }
		return render(http_request, 'pyha/base/index.html', context)










