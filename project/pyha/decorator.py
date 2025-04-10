from functools import wraps
from pyha.login import is_admin
from django.http import HttpResponse, HttpResponseNotAllowed
from django.utils import translation
from django.core.cache import caches
import inspect
import copy


def allowed_methods(allowed):
  def inner(fn):
    @wraps(fn)
    def wrapped(http_request, *args, **kwargs):
        if http_request.method not in allowed:
            return HttpResponseNotAllowed(allowed)

        return fn(http_request, *args, **kwargs)
    return wrapped
  return inner


def cached(timeout=300, cache_type='default'):
  def inner(fn):
    @wraps(fn)
    def wrapped(*args, refresh_cache=False, **kwargs):
        cache = caches[cache_type]
        cache_key = _generate_cache_key(fn, *args, **kwargs)
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
        if is_admin(request):
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

def _generate_cache_key(fn, *args, **kwargs):
    cache_key = fn.__name__

    named_args = {}
    arg_list = list(args) if args is not None else []
    fn_named_args = inspect.getfullargspec(fn).args
    remaining_kwargs = copy.copy(kwargs)

    for i, arg in enumerate(fn_named_args):
        arg_value = None
        if i < len(arg_list):
            arg_value = arg_list[i]
        elif arg in remaining_kwargs:
            arg_value = remaining_kwargs[arg]
            del remaining_kwargs[arg]

        named_args[arg] = arg_value

    extra_args = args[len(fn_named_args):]

    cache_key += _tuple_to_string(tuple(named_args.items()))
    cache_key += _tuple_to_string(tuple(extra_args))
    cache_key += _tuple_to_string(tuple(sorted(remaining_kwargs.items())))

    return cache_key.replace(' ', '_')


def _tuple_to_string(obj):
    if not isinstance(obj, tuple):
        return str(obj)

    return '({})'.format(','.join([_tuple_to_string(x) for x in obj]))


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
