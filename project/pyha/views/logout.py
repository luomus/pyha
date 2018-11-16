from django.http import HttpResponseRedirect
from pyha.login import log_out
from pyha.login import logged_in, _process_auth_response
from django.conf import settings

def logout(request):
    if not logged_in(request):
        return _process_auth_response(request, '')
    log_out(request)
    return HttpResponseRedirect("https://beta.laji.fi/")
    
def change_role(request):
    if not logged_in(request) and not 'role' in request.POST:
        return HttpResponseRedirect('/')
    nextRedirect = request.POST.get('next', '/pyha/')
    if(request.POST['role'] in request.session.get("user_roles", [None])):
        request.session['current_user_role'] = request.POST['role']
    return HttpResponseRedirect(nextRedirect)

def change_lang(request):
    if not logged_in(request) and not 'lang' in request.POST:
        return HttpResponseRedirect('/')
    nextRedirect = request.POST.get('next', '/pyha/')
    if(request.POST.get('language', 'none') in [x[0] for x in settings.LANGUAGES]):
        request.session["_language"] = request.POST['language']
    return HttpResponseRedirect(nextRedirect)