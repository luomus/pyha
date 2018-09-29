#coding=utf-8
from argparse import Namespace
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
from itertools import chain
from pyha.localization import translate_truth
from requests.auth import HTTPBasicAuth
from.models import Collection
from.models import Request
import json
import os
import requests

def store(jsond):
	if not checkJson(jsond):
		return
	data = json.loads(jsond, object_hook=lambda d: Namespace(**d))
	if Request.requests.filter(lajiId=os.path.basename(str(data.id))).exists():
		return
	status = getattr(data,'status', 0)
	time = datetime.now()
	
	req = Request()
	req.description=''
	req.lajiId = os.path.basename(str(data.id))
	req.status = status
	req.sensstatus = 99 if settings.SKIP_OFFICIAL else 0
	req.date = time
	req.source = data.source
	req.user = data.personId
	req.approximateMatches = data.approximateMatches
	req.downloadFormat = getattr(data,'downloadFormat','UNKNOWN')
	req.downloadIncludes = getattr(data,'downloadIncludes','UNKNOWN')
	req.filter_list = makeblob(data.filters)

	req.save()

	if hasattr(data, 'collections'):
		for i in data.collections:
				makeCollection(req, i)
	if hasattr(data, 'locale'):
		req.lang = data.locale
	else:
		req.lang = 'fi'
		
	return req

def makeCollection(req, i):
	co = Collection()
	co.address = i.id
	co.count = getattr(i, 'count', 0)
	co.status = 0
	co.request = req
	co.downloadRequestHandler = getattr(i, 'downloadRequestHandler', requests.get(settings.LAJIAPI_URL+"collections/"+str(co.address)+"?access_token="+settings.LAJIAPI_TOKEN).json().get('downloadRequestHandler',['none']))
	co.taxonSecured = getattr(i, 'conservationReasonCount', 0)
	co.customSecured = getattr(i, 'customReasonCount', 0)
	co.save()

def checkJson(jsond):
	wantedFields = ['"id":','"source":','"personId":','"approximateMatches":','"filters":'] 
	if all(x in jsond for x in wantedFields):
		return True
	return False
		
def makeblob(x):
	data = {}
	for i in x:
		for j in i.__dict__:
			data[j] = getattr(i, j)
	blob = json.dumps(data)
	return blob
	
def get_values_for_collections(requestId, request, List):
	for i, c in enumerate(List):
		if 'has expired' in cache.get(str(c)+'collection_values'+request.LANGUAGE_CODE, 'has expired'):
			c.result = requests.get(settings.LAJIAPI_URL+"collections/"+str(c)+"?lang=" + request.LANGUAGE_CODE + "&access_token="+settings.LAJIAPI_TOKEN).json()
			cache.set(str(c)+'collection_values'+request.LANGUAGE_CODE, c.result)
			c.result["collectionName"] = c.result.get("collectionName",c.address)
			c.result["description"] = c.result.get("description","-")
		else:
			c.result = cache.get(str(c)+'collection_values'+request.LANGUAGE_CODE)
			c.result["collectionName"] = c.result.get("collectionName",c.address)
			c.result["description"] = c.result.get("description","-")

def get_result_for_target(request, l):
	if 'has expired' in cache.get(str(l.target)+'collection_values'+request.LANGUAGE_CODE, 'has expired'):
		l.result = requests.get(settings.LAJIAPI_URL+"collections/"+str(l.target)+"?lang=" + request.LANGUAGE_CODE + "&access_token="+settings.LAJIAPI_TOKEN).json()
		cache.set(str(l.target)+'collection_values'+request.LANGUAGE_CODE, l.result)
		l.result["collectionName"] = l.result.get("collectionName",l.target)
	else:
		l.result = cache.get(str(l.target)+'collection_values'+request.LANGUAGE_CODE)
		l.result["collectionName"] = l.result.get("collectionName",l.target)
		
	
def fetch_user_name(personId):
	'''
	fetches user name for a person registered in Laji.fi
	:param personId: person identifier 
	:returns: person's full name
	'''
	username = 'pyha'
	password = settings.LAJIPERSONAPI_PW 
	if 'has expired' in cache.get('name'+personId, 'has expired'):
		response = requests.get(settings.LAJIPERSONAPI_URL+personId+"?format=json", auth=HTTPBasicAuth(username, password ))
		if(response.status_code == 200):
			data = response.json()
			name = data['rdf:RDF']['MA.person']['MA.fullName']
			cache.set('name'+personId,name)
			return name
		else:
			cache.set('name'+personId,personId)
			return personId
	else:
		return cache.get('name'+personId)

def fetch_role(personId):
	username = settings.LAJIPERSONAPI_USER
	password = settings.LAJIPERSONAPI_PW 
	if 'has expired' in cache.get('role'+personId, 'has expired'):
		response = requests.get(settings.LAJIPERSONAPI_URL+personId+"?format=json", auth=HTTPBasicAuth(username, password ))
		if(response.status_code == 200):
			data = response.json()
			role = data['rdf:RDF']['MA.person'].get('MA.role', {'role':'none'})
			cache.set('role'+personId,role)
			return role
	else:
		return cache.get('role'+personId)

def fetch_pdf(data,style):
	username = settings.PDFAPI_USER
	password = settings.PDFAPI_PW 
	if(style):
		data = "<div style='"+ style +"'>" + data +  "</div>"
	payload = {'html': data}
	response = requests.post(settings.PDFAPI_URL, data = payload, auth=HTTPBasicAuth(username, password ))
	if(response.status_code == 200):
		return response
	
def fetch_email_address(personId):
	'''
	fetches email-address for a person registered in Laji.fi
	:param personId: person identifier 
	:returns: person's email-address
	'''
	username = settings.LAJIPERSONAPI_USER
	password = settings.LAJIPERSONAPI_PW 
	if 'has expired' in cache.get('email'+personId, 'has expired'):
		response = requests.get(settings.LAJIPERSONAPI_URL+personId+"?format=json", auth=HTTPBasicAuth(username, password ))
		if(response.status_code == 200):
			data = response.json()
			email = data['rdf:RDF']['MA.person']['MA.emailAddress']
			cache.set('email'+personId,email)
			return email
		else:
			email = personId
			cache.set('email'+personId,email)
	else:
		return cache.get('email'+personId)


def create_coordinates(userRequest):
	filterList = json.loads(userRequest.filter_list, object_hook=lambda d: Namespace(**d))
	coord = getattr(filterList,"coordinates", None)
	if(coord):
		coordinates = coord[0].split(":", 4)
		coordinates = coordinates[:7]
		if(len(coordinates)>=4):
			coordinates.append("{:.6f}".format((float(coordinates[1])-float(coordinates[0]))/2 + float(coordinates[0])))
			coordinates.append("{:.6f}".format((float(coordinates[3])-float(coordinates[2]))/2 + float(coordinates[2])))
			return coordinates
	return None
	
def send_download_request(requestId):
	payload = {}
	userRequest = Request.requests.get(id=requestId)
	payload["id"] = userRequest.lajiId
	payload["personId"] = userRequest.user
	collectionlist = Collection.objects.filter(request=userRequest, status=4)
	if userRequest.sensstatus == 4:
		additionlist = Collection.objects.filter(request=userRequest, customSecured=0, taxonSecured__gt=0)
		collectionlist = list(chain(collectionlist, additionlist))
	cname = []
	for c in collectionlist:
		cname.append(c.address)
	payload["approvedCollections"] = cname
	payload["sensitiveApproved"] = "true"
	payload["secured"] = "true"
	payload["downloadFormat"] = "CSV_FLAT"
	payload["access_token"] = settings.LAJIAPI_TOKEN
	filters = json.loads(userRequest.filter_list, object_hook=lambda d: Namespace(**d))
	for f in filters.__dict__:
		payload[f] = getattr(filters, f)
	response = requests.post(settings.LAJIAPI_URL+"warehouse/private-query/downloadApproved", data=payload)

	
def show_filters(request, userRequest):
	'''
	Gathers all the names for the filters if available from Laji.api and reforms them into an usable list object. 
	Also contains them in a cache to lessen the laji.api strain.
	:param request: request identifier 
	:param userRequest: language code
	'''	
	filterList = json.loads(userRequest.filter_list, object_hook=lambda d: Namespace(**d))
	filterResultList = list(range(len(vars(filterList).keys())))
	lang = request.LANGUAGE_CODE
	if 'has expired' in cache.get('filters'+str(userRequest.id)+lang, 'has expired'):
		filters = requests.get(settings.LAJIFILTERS_URL)
		if(filters.status_code == 200):
			filtersobject = json.loads(filters.text, object_hook=lambda d: Namespace(**d))
			for i, b in enumerate(vars(filterList).keys()):
				languagelabel = b
				filternamelist = getattr(filterList, b)
				if isinstance(filternamelist, str):
					stringlist = []
					value = getattr(filterList, b)
					value = translate_truth(value, lang)
					stringlist.append(value)
					filternamelist = stringlist
				if b in filters.json():
					filterfield = getattr(filtersobject, b)
					label = getattr(filterfield, "label")
					if(lang == 'sw'):
						languagelabel = getattr(label, "sv")
					else:
						languagelabel = getattr(label, request.LANGUAGE_CODE)
					if "RESOURCE" in getattr(filterfield, "type"):
						resource = getattr(filterfield, "resource")
						for k, a in enumerate(getattr(filterList, b)):
							if resource.startswith("metadata"):
								filterfield2 = requests.get(settings.LAJIAPI_URL+str(resource)+"/?lang=" + request.LANGUAGE_CODE + "&access_token="+settings.LAJIAPI_TOKEN)
								filtername = str(a)
								for ii in filterfield2.json():
									if (str(a) == ii['id']):
										filtername = ii['value']
										break
							else:
								if(lang == 'sw'):
									filterfield2 = requests.get(settings.LAJIAPI_URL+str(resource)+"/"+str(a)+"?lang=sv&access_token="+settings.LAJIAPI_TOKEN)
								else:
									filterfield2 = requests.get(settings.LAJIAPI_URL+str(resource)+"/"+str(a)+"?lang=" + request.LANGUAGE_CODE + "&access_token="+settings.LAJIAPI_TOKEN)
								filternameobject = json.loads(filterfield2.text, object_hook=lambda d: Namespace(**d))
								filtername = getattr(filternameobject, "name", str(a))
							filternamelist[k]= filtername
					if "ENUMERATION" in getattr(filterfield, "type"):
						enumerations = getattr(filterfield, "enumerations")
						for k, e in enumerate(getattr(filterList, b)):
							filtername = e
							for n in enumerations:
								if e == getattr(n, "name"):
									if(lang == 'sw'):
										filtername = getattr(n.label, "sv")
									else:
										filtername = getattr(n.label, lang)
									break
							filternamelist[k]= filtername
				tup = (b, filternamelist, languagelabel)
				filterResultList[i] = tup
			cache.set('filters'+str(userRequest.id)+lang,filterResultList)
		else:
			for i, b in enumerate(vars(filterList).keys()):
				languagelabel = b
				filternamelist = getattr(filterList, b)
				if isinstance(filternamelist, str):
					stringlist = []
					value = getattr(filterList, b)
					value = translate_truth(value, lang)
					stringlist.append(value)
					filternamelist = stringlist
				tup = (b, filternamelist, b)
				filterResultList[i] = tup
			return filterResultList
	else:
		return cache.get('filters'+str(userRequest.id)+lang)
	return filterResultList