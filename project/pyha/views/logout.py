from django.http import HttpResponseRedirect
from pyha.login import log_out

from pyha.login import logged_in, _process_auth_response

def logout(request):
        if not logged_in(request):
            return _process_auth_response(request, '')
        log_out(request)
        return HttpResponseRedirect("https://beta.laji.fi/")