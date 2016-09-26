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
		checkJson(jsond)
		x = json.loads(jsond, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
		if not None == Request.objects.filter(id=x.id).exists():
			return
		req = Request(x.id, datetime.now(), x.source, x.email, x.approximateMatches, x.filters)
		print(str(x.id) + x.source + x.email + str(x.approximateMatches) + str(x.filters))
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
		print("jee")

def checkJson(jsond):
		wantedFields = ['"id":','"source":','"email":','"approximateMatches":','"filters":', '"collections":',] 
		if all(x in jsond for x in wantedFields):
			print 'missing fields'
			return false
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
