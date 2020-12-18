#coding=utf-8
from argparse import Namespace
from datetime import datetime
from django.conf import settings
from django.core.cache import cache, caches
from django.utils.translation import ugettext
from itertools import chain
from pyha.localization import translate_truth
from requests.auth import HTTPBasicAuth
from pyha.models import Request, Collection, StatusEnum, Col_StatusEnum, HandlerInRequest
from pyha.log_utils import changed_by
from pyha.utilities import Container
import json
import os
import requests

def store(jsond):
    if not checkJson(jsond):
        return
    data = json.loads(jsond, object_hook=lambda d: Namespace(**d))
    if Request.objects.filter(lajiId=os.path.basename(str(data.id))).exists():
        return
    status = getattr(data,'status', 0)
    time = datetime.now()

    req = Request()
    req.description=''
    req.lajiId = os.path.basename(str(data.id))
    req.status = status
    req.date = time
    req.source = data.source
    req.user = data.personId
    req.approximateMatches = data.approximateMatches
    req.downloadFormat = getattr(data,'downloadFormat','UNKNOWN')
    req.downloadIncludes = getattr(data,'downloadIncludes','UNKNOWN')
    req.downloaded = False
    req.filter_list = makeblob(data.filters)
    req.filter_description_list = namespace_to_json(data, 'filterDescriptions')
    if hasattr(data, 'locale'):
        req.lang = data.locale
    else:
        req.lang = u'fi'
    req.changedBy = changed_by("pyha")
    req.save()

    if hasattr(data, 'collections'):
        for i in data.collections:
                makeCollection(req, i)

    return req

def makeCollection(req, i):
    co = Collection()
    co.address = i.id
    co.status = 0
    co.request = req
    co.downloadRequestHandler = getattr(i, 'downloadRequestHandler', requests.get(settings.LAJIAPI_URL+"collections/"+str(co.address)+"?access_token="+settings.LAJIAPI_TOKEN, timeout=settings.SECRET_TIMEOUT_PERIOD).json().get('downloadRequestHandler',['none']))

    # old counts, may be removed in the future
    co.count = getattr(i, 'count', 0)
    co.taxonSecured = getattr(i, 'conservationReasonCount', 0)
    co.customSecured = getattr(i, 'customReasonCount', 0)
    co.quarantineSecured = getattr(i, 'dataQuarantineReasonCount', 0)

    co.count_list = namespace_to_json(i, 'counts')
    co.changedBy = changed_by("pyha")
    co.save()

def checkJson(jsond):
    wantedFields = ['"id":','"source":','"personId":','"approximateMatches":','"filters":']
    if all(x in jsond for x in wantedFields):
        return True
    return False

def namespace_to_json(data, attribute):
    value = getattr(data, attribute, None)
    if value is not None:
        return json.dumps(value, default=lambda o: o.__dict__)
    else:
        return ''

def makeblob(x):
    data = {}
    for i in x:
        for j in i.__dict__:
            data[j] = getattr(i, j)
    blob = json.dumps(data)
    return blob

def get_values_for_collections(requestId, http_request, list):
    for i, c in enumerate(list):
        if 'has expired' in cache.get(str(c.address)+'collection_values'+http_request.LANGUAGE_CODE, 'has expired'):
            try:
                c.result = requests.get(settings.LAJIAPI_URL+"collections/"+str(c.address)+"?lang=" + http_request.LANGUAGE_CODE + "&access_token="+settings.LAJIAPI_TOKEN, timeout=settings.SECRET_TIMEOUT_PERIOD).json()
            except:
                c.result = cache.get(str(c.address)+'collection_values'+http_request.LANGUAGE_CODE)
                c.result["collectionName"] = c.result.get("collectionName",c.address)
                c.result["description"] = c.result.get("description","-")
                c.result["qualityDescription"] = c.result.get("dataQualityDescription","-")
                c.result["collectionTerms"] = c.result.get("dataUseTerms","-")
                return
            cache.set(str(c.address)+'collection_values'+http_request.LANGUAGE_CODE, c.result)
            c.result["collectionName"] = c.result.get("collectionName",c.address)
            c.result["description"] = c.result.get("description","-")
            c.result["qualityDescription"] = c.result.get("dataQualityDescription","-")
            c.result["collectionTerms"] = c.result.get("dataUseTerms","-")
        else:
            c.result = cache.get(str(c.address)+'collection_values'+http_request.LANGUAGE_CODE)
            c.result["collectionName"] = c.result.get("collectionName",c.address)
            c.result["description"] = c.result.get("description","-")
            c.result["qualityDescription"] = c.result.get("dataQualityDescription","-")
            c.result["collectionTerms"] = c.result.get("dataUseTerms","-")

def get_result_for_target(http_request, l):
    if 'has expired' in cache.get(str(l.target)+'collection_values'+http_request.LANGUAGE_CODE, 'has expired'):
        try:
            l.result = requests.get(settings.LAJIAPI_URL+"collections/"+str(l.target)+"?lang=" + http_request.LANGUAGE_CODE + "&access_token="+settings.LAJIAPI_TOKEN, timeout=settings.SECRET_TIMEOUT_PERIOD).json()
        except:
            l.result = cache.get(str(l.target)+'collection_values'+http_request.LANGUAGE_CODE)
            l.result["collectionName"] = l.result.get("collectionName",l.target)
            return
        cache.set(str(l.target)+'collection_values'+http_request.LANGUAGE_CODE, l.result)
        l.result["collectionName"] = l.result.get("collectionName",l.target)
    else:
        l.result = cache.get(str(l.target)+'collection_values'+http_request.LANGUAGE_CODE)
        l.result["collectionName"] = l.result.get("collectionName",l.target)


def fetch_user_name(personId):
    '''
    fetches user name for a person registered in Laji.fi
    :param personId: person identifier
    :returns: person's full name
    '''
    username = settings.LAJIPERSONAPI_USER
    password = settings.LAJIPERSONAPI_PW
    cacheKeyPersonId = personId.replace(' ', '_')
    if 'has expired' in cache.get('name'+cacheKeyPersonId, 'has expired'):
        try:
            response = requests.get(settings.LAJIPERSONAPI_URL+personId+"?format=json", auth=HTTPBasicAuth(username, password ), timeout=settings.SECRET_TIMEOUT_PERIOD)
        except:
            response = Container()
            response.status_code = 500
        if(response.status_code == 200):
            data = response.json()
            name = data['rdf:RDF']['MA.person']['MA.fullName']
            cache.set('name'+cacheKeyPersonId,name)
            return name
        else:
            cache.set('name'+cacheKeyPersonId,personId)
            return personId
    else:
        return cache.get('name'+cacheKeyPersonId)

def fetch_role(personId):
    username = settings.LAJIPERSONAPI_USER
    password = settings.LAJIPERSONAPI_PW
    cacheKeyPersonId = personId.replace(' ', '_')
    if 'has expired' in cache.get('role'+cacheKeyPersonId, 'has expired'):
        response = requests.get(settings.LAJIPERSONAPI_URL+personId+"?format=json", auth=HTTPBasicAuth(username, password ), timeout=settings.SECRET_TIMEOUT_PERIOD)
        if(response.status_code == 200):
            data = response.json()
            role = data['rdf:RDF']['MA.person'].get('MA.role', {'role':'none'})
            cache.set('role'+cacheKeyPersonId,role)
            return role
    else:
        return cache.get('role'+cacheKeyPersonId)

def fetch_pdf(data,style):
    if(style):
        data = "<div style='"+ style +"'>" + data +  "</div>"
    response = requests.post(
        settings.LAJIAPI_URL+"html-to-pdf",
        data=data.encode("utf-8"),
        params={"access_token": settings.LAJIAPI_TOKEN},
        timeout=settings.SECRET_TIMEOUT_PERIOD,
        headers={"Content-Type": "text/plain; charset=utf-8"}
    )
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
    cacheKeyPersonId = personId.replace(' ', '_')
    if 'has expired' in cache.get('email'+cacheKeyPersonId, 'has expired'):
        try:
            response = requests.get(settings.LAJIPERSONAPI_URL+personId+"?format=json", auth=HTTPBasicAuth(username, password ), timeout=settings.SECRET_TIMEOUT_PERIOD)
        except:
            response = Container()
            response.status_code = 500
        if(response.status_code == 200):
            data = response.json()
            person_data = data['rdf:RDF']['MA.person']
            if 'MA.emailAddress' in person_data:
                email = person_data['MA.emailAddress']
                cache.set('email'+cacheKeyPersonId,email)
                return email

        email = personId
        cache.set('email'+cacheKeyPersonId,email)
        return email
    else:
        return cache.get('email'+cacheKeyPersonId)


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
    userRequest = Request.objects.get(id=requestId)
    payload["id"] = userRequest.lajiId
    payload["personId"] = userRequest.user
    collectionlist = Collection.objects.filter(request=userRequest).exclude(status=Col_StatusEnum.APPROVED)
    cname = []
    for c in collectionlist:
        cname.append(c.address)
    payload["rejectedCollections"] = cname
    payload["sensitiveApproved"] = "true"
    payload["downloadFormat"] = userRequest.downloadFormat
    payload["downloadIncludes"] = userRequest.downloadIncludes
    payload["access_token"] = settings.LAJIAPI_TOKEN
    filters = json.loads(userRequest.filter_list, object_hook=lambda d: Namespace(**d))
    for f in filters.__dict__:
        payload[f] = getattr(filters, f)
    response = requests.post(settings.LAJIAPI_URL+"warehouse/private-query/downloadApproved", data=payload, timeout=settings.SECRET_TIMEOUT_PERIOD)

def update_collections():
    payload = {}
    payload['access_token'] = settings.LAJIAPI_TOKEN
    payload['pageSize'] = 1000
    payload['page'] = 1
    notFinished = True
    result = []
    while notFinished:
        try:
            response = requests.get(settings.LAJIAPI_URL+"collections", params=payload, timeout=settings.SECRET_TIMEOUT_PERIOD)
        except:
            response = Container()
            response.status_code = 500
        if(response.status_code == 200):
            data = response.json()
        else:
            caches['collections'].set('collection_update','updated', 7200)
            return False
        for co in data['results']:
            if not "MY.metadataStatusHidden" in co.get('MY.metadataStatus', {}):
                result.append(co)
        if payload['page'] < data['lastPage']:
            payload['page'] += 1
        else:
            notFinished = False
    caches['collections'].set('collections',result)
    caches['collections'].set('collection_update','updated', 7200)
    return True

def get_download_handlers_where_collection(collectionId):
    result = {}
    collections = caches['collections'].get('collections')
    for co in collections:
        if co['id'] == collectionId:
            result = co.get('downloadRequestHandler', {})
            break
    return result

def get_contact_email_for_collection(collectionId):
    result = None
    collections = caches['collections'].get('collections')
    for co in collections:
        if co['id'] == collectionId:
            result = co.get('contactEmail', None)
            break
    return result

def get_collections_where_download_handler(userId):
    resultlist = []
    collections = caches['collections'].get('collections')
    for co in collections:
        if userId in co.get('downloadRequestHandler', {}):
            resultlist.append(co['id'])
    return resultlist

def get_download_handlers_with_collections_listed_for_collections(requestId, collectionsList):
    resultlist = []
    collections = caches['collections'].get('collections')
    collections = [co for co in collections if co['id'] in [coli.address for coli in collectionsList]]
    repeatedhandlers = [co.get('downloadRequestHandler', ['None']) for co in collections]
    handlers = set(chain(*repeatedhandlers))
    handlerswithcollections = []
    for ha in handlers:
        handlerswithcollections.append({"handlers": [{"name":ha,"id":ha,"email":'undefined'}], "collections":[co for co in collections if ha in co.get('downloadRequestHandler', ['None'])]})

    emailed_handlers = HandlerInRequest.objects.filter(request=requestId)
    for hanco in handlerswithcollections:
        hanco["handlers"][0]["mailed"] = False
        for handler in emailed_handlers:
            if hanco["handlers"][0]["id"] == handler.user:
                if handler.emailed: hanco["handlers"][0]["mailed"] = True
                break

    noneindex = -1
    for index, hanco in enumerate(handlerswithcollections):
        if(hanco["handlers"][0]["id"] != 'None'):
            hanco["handlers"][0]["name"] = fetch_user_name(hanco["handlers"][0]["id"])
            hanco["handlers"][0]["email"] = fetch_email_address(hanco["handlers"][0]["id"])
        else:
            noneindex = index
    if noneindex > -1:
        handlerswithcollections.insert(0, handlerswithcollections.pop(noneindex))

    #Groups handlers with identical collections
    while(True):
        grouped = False
        for i in range(0, len(handlerswithcollections)):
            for j in range(i+1, len(handlerswithcollections)):
                if handlerswithcollections[i]['collections'] == handlerswithcollections[j]['collections']:
                    handlerswithcollections[i]["handlers"] = handlerswithcollections[i]["handlers"] + (handlerswithcollections[j]["handlers"])
                    handlerswithcollections.remove(handlerswithcollections[j])
                    grouped = True
                    break
            if grouped: break
        if not grouped: break
    return handlerswithcollections

def is_collections_missing_download_handler(collectionsList):
    collections = caches['collections'].get('collections')
    collections = [co for co in collections if co['id'] in [coli.address for coli in collectionsList]]
    missing = False;
    for co in collections:
        if 'None' == co.get('downloadRequestHandler', ['None'])[0]:
            missing = True
            break
    return missing


def is_download_handler(userId):
    return len(get_collections_where_download_handler(userId)) > 0

def is_download_handler_in_collection(userId, collectionId):
    collections = caches['collections'].get('collections')
    for co in collections:
        if co['id'] == collectionId:
            if userId in co.get('downloadRequestHandler', {}):
                return True
            else:
                return False
    return False

def get_collection_counts(collection, http_request):
    lang = http_request.LANGUAGE_CODE

    if len(collection.count_list) == 0:
        result = []
        if collection.quarantineSecured > 0:
            result.append({
              'label': ugettext('secured_by_quarantine'),
              "count": collection.quarantineSecured
            })
        if collection.taxonSecured > 0:
            result.append({
              'label': ugettext('secured_by_sensitivity'),
              "count": collection.taxonSecured
            })
        if collection.customSecured > 0:
            result.append({
              'label': ugettext('secured_by_data_provider'),
              "count": collection.customSecured
            })

        return result

    count_list = json.loads(collection.count_list)
    for count in count_list:
        count['label'] = count['label'][lang]
    return count_list

def show_filters(http_request, userRequest):
    '''
    Gathers all the names for the filters if available from Laji.api and reforms them into an usable list object.
    Also contains them in a cache to lessen the laji.api strain.
    :param request: request identifier
    :param userRequest: language code
    '''
    filterList = json.loads(userRequest.filter_list, object_hook=lambda d: Namespace(**d))
    filterResultList = list(range(len(vars(filterList).keys())))
    lang = http_request.LANGUAGE_CODE
    if 'has expired' in cache.get('filters'+str(userRequest.id)+lang, 'has expired'):
        try:
            filters = requests.get(settings.LAJIFILTERS_URL, timeout=settings.SECRET_TIMEOUT_PERIOD)
        except:
            filters = Container()
            filters.status_code = 500
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
                    languagelabel = getattr(label, http_request.LANGUAGE_CODE)
                    if "RESOURCE" in getattr(filterfield, "type"):
                        resource = getattr(filterfield, "resource")
                        for k, a in enumerate(filternamelist):
                            if resource.startswith("metadata"):
                                filterfield2 = requests.get(settings.LAJIAPI_URL+str(resource)+"/?lang=" + http_request.LANGUAGE_CODE + "&access_token="+settings.LAJIAPI_TOKEN, timeout=settings.SECRET_TIMEOUT_PERIOD)
                                filtername = str(a)
                                for ii in filterfield2.json():
                                    if (str(a) == ii['id']):
                                        filtername = ii['value']
                                        break
                            else:
                                filterfield2 = requests.get(settings.LAJIAPI_URL+str(resource)+"/"+str(a)+"?lang=" + http_request.LANGUAGE_CODE + "&access_token="+settings.LAJIAPI_TOKEN, timeout=settings.SECRET_TIMEOUT_PERIOD)
                                filternameobject = json.loads(filterfield2.text, object_hook=lambda d: Namespace(**d))
                                filtername = getattr(filternameobject, "name", str(a))
                            filternamelist[k]= filtername
                    if "ENUMERATION" in getattr(filterfield, "type"):
                        enumerations = getattr(filterfield, "enumerations")
                        for k, e in enumerate(filternamelist):
                            filtername = e
                            for n in enumerations:
                                if e == getattr(n, "name"):
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
