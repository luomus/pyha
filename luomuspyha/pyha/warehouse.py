import requests
from datetime import datetime
from django.shortcuts import redirect
from django.conf import settings
from django.db import models
import json
from.models import Request
from.models import Collection
from argparse import Namespace


def store(jsond):
		if not checkJson(jsond):
			return
		x = json.loads(jsond, object_hook=lambda d: Namespace(**d))
		if Request.requests.filter(id=x.id).exists():
			return
		order = Request.requests.filter(email=x.email).count() + 1
		b = json.loads(makefiltersblob(x), object_hook=lambda d: Namespace(**d))
		req = Request(x.id, order, datetime.now(), x.source, x.email, x.approximateMatches, makefiltersblob(x))
		req.save()
		b = json.loads(makefiltersblob(x), object_hook=lambda d: Namespace(**d))
		print getattr(b, vars(b).keys()[1])[0]
		for i in x.collections:
			co = Collection()
			co.name = ""
			co.collection_id = i.id
			co.count = i.count
			co.request = req
			co.save()

def checkJson(jsond):
		wantedFields = ['"id":','"source":','"email":','"approximateMatches":','"filters":', '"collections":',] 
		if all(x in jsond for x in wantedFields):
			return True
		print 'missing fields'
		return False
		
def makefiltersblob(x):
		blob = "{"
		for i, text in enumerate(x.filters):
			if not(i == 0):
					blob += ","
			blob += '"' + str(vars(x.filters[i]).keys()[0]) + '":['
			for l,text in enumerate(getattr(x.filters[i], vars(x.filters[i]).keys()[0])):
				if not(l == 0):
					blob += ","
				blob += '"'+str(text)+'"'
			blob += "]"
		blob += "}"
		return blob
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
