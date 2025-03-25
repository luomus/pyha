from functools import wraps
from pyha.login import is_admin
from django.http import HttpResponse
from django.utils import translation
from django.core.cache import cache


def cached(timeout=300):
  def inner(fn):
    @wraps(fn)
    def wrapped(*args, refresh_cache=False, **kwargs):
        cache_key = str(fn.__name__) + str(args) + str(kwargs)
        cache_not_found = 'not found in cache'

        cached_result = cache.get(cache_key, cache_not_found) if not refresh_cache else cache_not_found
        if cached_result != cache_not_found:
            return cached_result

        result = fn(*args, **kwargs)
        cache.set(cache_key, result, timeout=timeout)
        return result
    return wrapped
  return inner

def admin_required_and_force_english(function):
    @wraps(function)
    def check_admin_with_english(request, *args, **kwargs):
        if(is_admin(request)):
            translation.activate("en")
            return function(request, *args, **kwargs)
        else:
            return HttpResponse(status=404)
    return check_admin_with_english


def required(wrapping_functions, patterns_rslt):
    '''
    Used to require 1..n decorators in any view returned by a url tree

    Usage:
      urlpatterns = required(func,patterns(...))
      urlpatterns = required((func,func,func),patterns(...))

    Note:
      Use functools.partial to pass keyword params to the required 
      decorators. If you need to pass args you will have to write a 
      wrapper function.

    Example:
      from functools import partial

      urlpatterns = required(
          partial(login_required,login_url='/accounts/login/'),
          patterns(...)
      )
    '''
    if not hasattr(wrapping_functions, '__iter__'):
        wrapping_functions = (wrapping_functions,)

    return [
        _wrap_instance__resolve(wrapping_functions, instance)
        for instance in patterns_rslt
    ]


def _wrap_instance__resolve(wrapping_functions, instance):
    if not hasattr(instance, 'resolve'):
        return instance
    resolve = getattr(instance, 'resolve')

    def _wrap_func_in_returned_resolver_match(*args, **kwargs):
        rslt = resolve(*args, **kwargs)

        if not hasattr(rslt, 'func'):
            return rslt
        f = getattr(rslt, 'func')

        for _f in reversed(wrapping_functions):
            # @decorate the function from inner to outter
            f = _f(f)

        setattr(rslt, 'func', f)

        return rslt

    setattr(instance, 'resolve', _wrap_func_in_returned_resolver_match)

    return instance
