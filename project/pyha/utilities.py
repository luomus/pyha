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