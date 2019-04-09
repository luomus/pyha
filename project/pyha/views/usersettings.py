import time
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
def usersettings(http_request):
	if check_language(http_request):
		return HttpResponseRedirect(http_request.get_full_path())
	if not logged_in(http_request):
		return _process_auth_response(http_request,'')
	if not ADMIN in http_request.session.get("current_user_role", [None]):
		return HttpResponseRedirect(reverse('pyha:root'))
	userId = http_request.session["user_id"]
	hasRoleHeader = any([role in http_request.session.get("user_roles", [None]) for role in ROLES_SHOWN_ROLE_IN_HEADER])
	toast = None
	if(http_request.session.get("toast", None) is not None): 
		toast = http_request.session["toast"]
		http_request.session["toast"] = None
		http_request.session.save()
	context = {"username": http_request.session["user_name"],"role": hasRoleHeader,"static": settings.STA_URL}
	return render(http_request, 'pyha/base/usersettings.html', context)











