#coding=utf-8
import requests
from datetime import datetime
from django.shortcuts import redirect
from django.conf import settings
from django.db import models
from django.core.mail import send_mail
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
		order = Request.requests.filter(user=x.personId).count() + 1
		status = getattr(x,'status', 0)
		time = datetime.now()
		req = Request()
		req.id = os.path.basename(str(x.id))
		req.description = description
		req.order = order
		req.status = status
		req.sensstatus = 0
		req.date = time
		req.source = x.source
		req.user = x.personId
		req.approximateMatches = x.approximateMatches
		req.downloadFormat = getattr(x,'downloadFormat','UNKNOWN')
		req.downloadIncludes = getattr(x,'downloadIncludes','UNKNOWN')
		req.filter_list = makeblob(x.filters)

		req.save()
		if hasattr(x, 'collections'):
                        for i in x.collections:
                                co = Collection()
                                co.collection_id = os.path.basename(str(i.id))
                                co.description = 'kuvaus'
                                co.count = getattr(i, 'count', 0)
                                co.secureReasons = getattr(i, 'secureReasons', "none")
                                co.status = 0
                                co.request = req
                                co.save()
		make_mail(x, time)

def make_mail(x, time):
		subject = getattr(x, 'description', time.strftime('%d.%m.%Y %H:%I'))
		req_order = Request.requests.filter(user=x.personId).count()
		req_link = settings.REQ_URL+str(req_order)
		message_content = u"Olette tehneet pyynnön salattuun aineistoon Lajitietokeskuksessa "+time.strftime('%d.%m.%Y %H:%I')+u".\nPyyntö tarvitsee teiltä vielä ehtojen hyväksynnän.\nOsoite aineistopyyntöön "+subject+": "+req_link+ "\n\nYou have made a request to download secure FinBIF data on "+time.strftime('%d.%m.%Y %H:%I')+".\nYou are required to agree to the terms of use.\nAddress to your request "+subject+": "+req_link 
		message = message_content
		from_email = 'helpdesk@laji.fi'
		recipients = [x.email]
		mail = send_mail(subject, message, from_email, recipients, fail_silently=False)
		return mail

def checkJson(jsond):
		wantedFields = ['"id":','"source":','"email":','"personId":','"approximateMatches":','"filters":'] 
		if all(x in jsond for x in wantedFields):
			return True
		return False
		
def makeblob(x):
		blob = "{"
		for i, text in enumerate(x):
			if not(i == 0):
					blob += ","
			blob += '"' + list(vars(x[i]).keys())[0] + '":['
			if isinstance(getattr(x[i], list(vars(x[i]).keys())[0]), (list)):
				for l,text in enumerate(getattr(x[i], list(vars(x[i]).keys())[0])):
					if not(l == 0):
						blob += ","
					blob += '"'+text+'"'
			else:
				blob += '"'+getattr(x[i], list(vars(x[i]).keys())[0])+'"'
			blob += "]"
		blob += "}"
		return blob
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
