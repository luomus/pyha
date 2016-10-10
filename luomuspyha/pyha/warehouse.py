import requests
from datetime import datetime
from django.shortcuts import redirect
from django.conf import settings
from django.db import models
import json
import os
from.models import Request
from.models import Collection
from argparse import Namespace
from random import randint

def store(jsond):
		if not checkJson(jsond):
			return
		x = json.loads(jsond, object_hook=lambda d: Namespace(**d))
		if Request.requests.filter(id=os.path.basename(str(x.id))).exists():
			return
		description = 'kuvaus'
		order = Request.requests.filter(email=x.email).count() + 1
		status = randint(0,4)
		req = Request(os.path.basename(str(x.id)), description , order, status, datetime.now(), x.source, x.email, x.approximateMatches, getattr(x,'downloadFormat','UNKNOWN'), getattr(x,'downloadIncludes','UNKNOWN'), makefiltersblob(x))
		req.save()
		if hasattr(x, 'collections'):
                        for i in x.collections:
                                co = Collection()
                                co.collection_id = os.path.basename(str(i.id))
                                co.description = 'kuvaus'
                                co.count = getattr(i, 'count', 0)
                                co.status = randint(0,4)
                                co.request = req
                                co.save()

def checkJson(jsond):
		wantedFields = ['"id":','"source":','"email":','"approximateMatches":','"filters":'] 
		if all(x in jsond for x in wantedFields):
			return True
		return False
		
def makefiltersblob(x):
		blob = "{"
		for i, text in enumerate(x.filters):
			if not(i == 0):
					blob += ","
			blob += '"' + list(vars(x.filters[i]).keys())[0] + '":['
			if isinstance(getattr(x.filters[i], list(vars(x.filters[i]).keys())[0]), (list)):
				for l,text in enumerate(getattr(x.filters[i], list(vars(x.filters[i]).keys())[0])):
					if not(l == 0):
						blob += ","
					blob += '"'+text+'"'
			else:
				blob += '"'+getattr(x.filters[i], list(vars(x.filters[i]).keys())[0])+'"'
			blob += "]"
		blob += "}"
		return blob
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
