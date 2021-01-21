import json
import sys

class Container(object):
    pass

def get_callers_function_name():
    return sys._getframe(2).f_code.co_name

import traceback
try:
    from hashlib import md5
except ImportError:
    from md5 import md5
from datetime import datetime, timedelta


class EmailRateLimitFilter(object):

    _errors = {}

    def filter(self, record):
        from django.conf import settings
        from django.core.cache import caches

        if record.exc_info is None:
            return False

        tb = '\n'.join(traceback.format_exception(*record.exc_info))

        # Track duplicate errors
        duplicate = False
        rate = getattr(settings, 'ERROR_RATE_LIMIT', 1800)  # seconds
        if rate > 0:
            key = md5(tb.encode('utf-8')).hexdigest()
            prefix = getattr(settings, 'ERROR_RATE_CACHE_PREFIX', 'ERROR_RATE')

            # Test if the cache works
            cache_key = '%s_%s' % (prefix, key)
            try:
                caches['error_mail'].set(prefix, 1, 1)
                use_cache = caches['error_mail'].get(prefix) == 1
            except:
                use_cache = False

            if use_cache:
                duplicate = caches['error_mail'].get(cache_key) == 1
                if not duplicate:
                    caches['error_mail'].set(cache_key, 1, rate)
            else:
                min_date = datetime.now() - timedelta(seconds=rate)
                max_keys = getattr(settings, 'ERROR_RATE_KEY_LIMIT', 100)
                duplicate = (key in self._errors and self._errors[key] >= min_date)
                self._errors = dict(list(filter(lambda x: x[1] >= min_date,
                                          sorted(self._errors.items(),
                                                 key=lambda x: x[1])))[0-max_keys:])
                if not duplicate:
                    self._errors[key] = datetime.now()

        return not duplicate
