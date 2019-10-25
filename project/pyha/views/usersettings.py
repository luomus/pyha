from django.utils.translation import ugettext
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pyha.log_utils import changed_by_session_user, changed_by
from pyha.localization import check_language
from pyha.login import logged_in, _process_auth_response, is_admin
from pyha.models import AdminUserSettings, AdminPyhaSettings
from pyha.roles import ADMIN
from pyha import toast


@csrf_exempt
def usersettings(http_request):
	if check_language(http_request):
		return HttpResponseRedirect(http_request.get_full_path())
	if not logged_in(http_request):
		return _process_auth_response(http_request,'')
	if not ADMIN in http_request.session.get("current_user_role", [None]):
		return HttpResponseRedirect(reverse('pyha:root'))
	userId = http_request.session["user_id"]
	toast = None
	if(http_request.session.get("toast", None) is not None):
		toast = http_request.session["toast"]
		http_request.session["toast"] = None
		http_request.session.save()
	user_settings = AdminUserSettings.objects.filter(user=http_request.session["user_id"])
	pyha_settings = AdminPyhaSettings.objects.filter(settingsName = 'default')
	if not user_settings.exists():
		user_settings = AdminUserSettings()
		user_settings.user = http_request.session["user_id"]
		user_settings.changedBy = changed_by_session_user(http_request)
		user_settings.save()
	else:
		user_settings = user_settings.first()
	if not AdminPyhaSettings.objects.filter(settingsName = 'default').exists():
		pyha_settings = AdminPyhaSettings()
		pyha_settings.settingsName = 'default'
		pyha_settings.changedBy = changed_by("pyha")
		pyha_settings.save()
	else:
		pyha_settings = pyha_settings.first()
	context = {"pyha_settings":pyha_settings, "email_new_requests_setting":AdminUserSettings.EMAIL_NEW_REQUESTS_SETTING, "user_settings":user_settings, "toast": toast,"username": http_request.session["user_name"], "email": http_request.session["user_email"], "static": settings.STA_URL}
	return render(http_request, 'pyha/base/admin/usersettings.html', context)

def save_user_settings(http_request):
	if http_request.method == 'POST':
		nexturl = http_request.POST.get('next', '/')
		if not logged_in(http_request):
			return _process_auth_response(http_request, "pyha")
		if not is_admin(http_request):
			return HttpResponse(status=404)
		user_settings = AdminUserSettings.objects.get(user=http_request.session["user_id"])
		user_settings.emailNewRequests = http_request.POST.get('email_new_requests', AdminUserSettings.NONE)
		user_settings.enableCustomEmailAddress = http_request.POST.get('use_custom_email', False)
		user_settings.customEmailAddress = http_request.POST.get('email_address', None)
		user_settings.changedBy = changed_by_session_user(http_request)
		user_settings.save()
		http_request.session["toast"] = {"status": toast.POSITIVE , "message": ugettext('toast_user_settings_saved_succesfully')}

		return HttpResponseRedirect(nexturl)
	return HttpResponseRedirect(reverse('pyha:root'))

def save_pyha_settings(http_request):
	if http_request.method == 'POST':
		nexturl = http_request.POST.get('next', '/')
		if not logged_in(http_request):
			return _process_auth_response(http_request, "pyha")
		if not is_admin(http_request):
			return HttpResponse(status=404)
		pyha_settings = AdminPyhaSettings.objects.filter(settingsName = 'default')
		if pyha_settings.exists():
			pyha_settings = pyha_settings.first()
			pyha_settings.enableDailyHandlerEmail = http_request.POST.get('enable_daily_handler_email', False)
			pyha_settings.enableWeeklyMissingHandlersEmail = http_request.POST.get('enable_weekly_missing_handlers_email', False)
			pyha_settings.enableDeclineOverdueCollections = http_request.POST.get('enable_auto_decline_overdue', False)
			pyha_settings.changedBy = changed_by_session_user(http_request)
			pyha_settings.save()
			http_request.session["toast"] = {"status": toast.POSITIVE , "message": ugettext('toast_pyha_settings_saved_succesfully')}
		return HttpResponseRedirect(nexturl)
	return HttpResponseRedirect(reverse('pyha:root'))
