from django.http import HttpResponseRedirect
from pyha.login import log_out
from pyha.login import logged_in, _process_auth_response
from django.conf import settings


def logout(http_request):
    if not logged_in(http_request):
        return _process_auth_response(http_request, '')
    log_out(http_request)
    return HttpResponseRedirect(settings.AFTER_LOGOUT_URL)


def change_role(http_request):
    if not logged_in(http_request) and not 'role' in http_request.POST:
        return HttpResponseRedirect('/')
    nextRedirect = http_request.POST.get('next', '/pyha/')
    if(http_request.POST['role'] in http_request.session.get("user_roles", [None])):
        http_request.session['current_user_role'] = http_request.POST['role']
    return HttpResponseRedirect(nextRedirect)


def change_lang(http_request):
    if not logged_in(http_request) and not 'lang' in http_request.POST:
        return HttpResponseRedirect('/')
    nextRedirect = http_request.POST.get('next', '/pyha/')
    response = HttpResponseRedirect(nextRedirect)
    if(http_request.POST.get('language', 'none') in [x[0] for x in settings.LANGUAGES]):
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, http_request.POST['language'])
    return response
