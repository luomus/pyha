from pyha.utilities import get_callers_function_name

def changed_by(user):
    return '%s %s' %(user, get_callers_function_name())

def changed_by_session_user(request):
    return '%s %s' %(request.session["user_id"], get_callers_function_name())