import requests
from datetime import datetime
from django.shortcuts import redirect
from django.conf import settings
from django.db import models
from collections import namedtuple
import json
from.models import Request
from.models import Collection


def store(jsond):
		if not checkJson(jsond):
			return
		x = json.loads(jsond, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
		if Request.requests.filter(id=x.id).exists():
			return
		order = Request.requests.filter(email=x.email).count() + 1
		req = Request(x.id, order, datetime.now(), x.source, x.email, x.approximateMatches, x.filters)
		print(str(order))
		req.save()
		for i in x.collections:
			co = Collection()
			co.name = ""
			co.collection_id = i.id
			co.count = i.count
			co.request = req
			co.save()
			print(co)
			print(str(co.id))

def checkJson(jsond):
		wantedFields = ['"id":','"source":','"email":','"approximateMatches":','"filters":', '"collections":',] 
		if all(x in jsond for x in wantedFields):
			return True
		print 'missing fields'
		return False
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
