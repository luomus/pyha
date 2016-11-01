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
		req = Request(os.path.basename(str(x.id)), description , order, status, datetime.now(), x.source, x.personId, x.approximateMatches, getattr(x,'downloadFormat','UNKNOWN'), getattr(x,'downloadIncludes','UNKNOWN'), makefiltersblob(x))

		req.save()



		if hasattr(x, 'collections'):
                        for i in x.collections:
                        		makeCollection(req, i)
		make_mail(x)

def makeCollection(req, i):
		co = Collection()
		co.collection_id = os.path.basename(str(i.id))
		co.description = 'kuvaus'
		co.count = getattr(i, 'count', 0)
		co.status = 0
		co.request = req
		secureReasons = getattr(i, 'mainSecureReasons', 0)
		if(secureReasons != 0):
			taxon = getattr(secureReasons, 'DEFAULT_TAXON_CONSERVATION', 0)
			print(taxon)
			custom = getattr(secureReasons, 'CUSTOM', 0)
			if(taxon != 0):
				co.taxonSecured = getattr(taxon, 'count', 0)
			if(custom != 0):
				co.customSecured = getattr(custom, 'count', 0)
		co.save()


def make_mail(x):
		subject = getattr(x, 'description', str (datetime.now()))
		req_order = Request.requests.filter(user=x.personId).count()
		req_link = settings.REQ_URL+str(req_order)
		message_content = u"Aineistopyyntö odottaa kasittelyänne. Linkki aineistopyyntöönne "+subject+": "+req_link
		message = message_content
		from_email = 'messanger@localhost.com'
		recipients = ['x.email']
		mail = send_mail(subject, message, from_email, recipients, fail_silently=False)
		return mail

def checkJson(jsond):
		wantedFields = ['"id":','"source":','"email":','"personId":','"approximateMatches":','"filters":'] 
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
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
