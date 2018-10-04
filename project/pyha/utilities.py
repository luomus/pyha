import json
from argparse import Namespace

def filterlink(userRequest, request, filters, link):
	filterList = json.loads(userRequest.filter_list, object_hook=lambda d: Namespace(**d))
	first = True
	for f in vars(filterList).keys():
		if not first:
			link += "&"
		else:
			first = False
		link += f + "="
		if not isinstance(getattr(filterList, f), str):
			secondfirst = True
			for e in getattr(filterList, f):
				if not secondfirst:
					link += "%2C"
				link += e
		else:
			link += getattr(filterList, f)
	return link
	
	
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
                self._errors = dict(filter(lambda x: x[1] >= min_date,
                                          sorted(self._errors.items(),
                                                 key=lambda x: x[1]))[0-max_keys:])
                if not duplicate:
                    self._errors[key] = datetime.now()

        return not duplicate
