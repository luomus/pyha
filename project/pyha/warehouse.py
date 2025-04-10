# coding=utf-8
from argparse import Namespace
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from django.conf import settings
from django.core.cache import cache, caches
from django.utils.translation import ugettext
from itertools import chain
from requests.auth import HTTPBasicAuth

from pyha.collection_metadata import get_collections, get_collections_by_id_and_lang
from pyha.models import Request, Collection, Col_StatusEnum, HandlerInRequest
from pyha.log_utils import changed_by
from pyha.utilities import Container
from pyha.roles import HANDLER_ANY, ADMIN
import json
from json import JSONDecodeError
import os
import requests


def store(jsond):
    if not checkJson(jsond):
        return
    data = json.loads(jsond, object_hook=lambda d: Namespace(**d))
    if Request.objects.filter(lajiId=os.path.basename(str(data.id))).exists():
        return
    status = getattr(data, 'status', 0)
    time = datetime.now()

    req = Request()
    req.description = ''
    req.lajiId = os.path.basename(str(data.id))
    req.status = status
    req.date = time
    req.source = data.source
    req.user = data.personId
    req.approximateMatches = data.approximateMatches
    req.downloadFormat = getattr(data, 'downloadFormat', 'UNKNOWN')
    req.downloadIncludes = getattr(data, 'downloadIncludes', 'UNKNOWN')
    req.downloaded = False
    req.filter_list = makeblob(data.filters)
    req.filter_description_list = namespace_to_json(data, 'filterDescriptions')
    req.public_link = namespace_to_json(data, 'publicLink')
    req.private_link = namespace_to_json(data, 'privateLink')
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
    co.downloadRequestHandler = getattr(i, 'downloadRequestHandler', requests.get(settings.LAJIAPI_URL+"collections/"+str(
        co.address)+"?access_token="+settings.LAJIAPI_TOKEN, timeout=settings.SECRET_TIMEOUT_PERIOD).json().get('downloadRequestHandler', ['none']))

    # old counts, may be removed in the future
    co.count = getattr(i, 'count', 0)
    co.taxonSecured = getattr(i, 'conservationReasonCount', 0)
    co.customSecured = getattr(i, 'customReasonCount', 0)
    co.quarantineSecured = getattr(i, 'dataQuarantineReasonCount', 0)

    co.count_list = namespace_to_json(i, 'counts')
    count_sum = 0
    for count in getattr(i, 'counts', []):
        count_sum += count.count
    co.count_sum = count_sum
    co.changedBy = changed_by("pyha")
    co.save()


def checkJson(jsond):
    wantedFields = ['"id":', '"source":', '"personId":', '"approximateMatches":', '"filters":']
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


def get_values_for_collections(requestId, lang, collections):
    col_ids = [c.address for c in collections]
    data_by_id = get_collections_by_id_and_lang(col_ids, lang)

    for c in collections:
        if c.address in data_by_id:
            c.result = data_by_id[c.address]
        else:
            c.result = {}

        c.result["collectionName"] = c.result.get("collectionName", c.address)
        c.result["description"] = c.result.get("description", "-")
        c.result["qualityDescription"] = c.result.get("dataQualityDescription", "-")
        c.result["collectionTerms"] = c.result.get("dataUseTerms", "-")


def get_result_for_target(http_request, l):
    data = get_collections_by_id_and_lang([l.target, http_request.LANGUAGE_CODE])
    if l.target in data:
        l.result = data[l.target]
        l.result["collectionName"] = l.result.get("collectionName", l.target)
    else:
        l.result = {"collectionName": l.target}


def fetch_user_name(user_id):
    '''
    fetches user name for a person registered in Laji.fi
    :param personId: person identifier
    :returns: person's full name
    '''
    return fetch_user_info([user_id])[user_id].name


def fetch_role(personId):
    username = settings.LAJIPERSONAPI_USER
    password = settings.LAJIPERSONAPI_PW
    cacheKeyPersonId = personId.replace(' ', '_')
    if 'has expired' in cache.get('role'+cacheKeyPersonId, 'has expired'):
        response = requests.get(settings.LAJIPERSONAPI_URL+personId+"?format=json",
                                auth=HTTPBasicAuth(username, password), timeout=settings.SECRET_TIMEOUT_PERIOD)
        if(response.status_code == 200):
            data = response.json()
            role = data['rdf:RDF']['MA.person'].get('MA.role', {'role': 'none'})
            cache.set('role'+cacheKeyPersonId, role)
            return role
    else:
        return cache.get('role'+cacheKeyPersonId)


def fetch_pdf(data, style):
    if style:
        data = (
        "<!DOCTYPE html>"
        "<html>"
        "<head>"
            "<meta charset='UTF-8'>"
            "<style>" + style + "</style>"
        "</head>"
        "<body>" + data + "</body>"
        "</html>"
        )

    response = requests.post(
        settings.LAJIAPI_URL+"html-to-pdf",
        data=data.encode("utf-8"),
        params={"access_token": settings.LAJIAPI_TOKEN},
        timeout=settings.SECRET_TIMEOUT_PERIOD,
        headers={"Content-Type": "text/plain; charset=utf-8"}
    )

    if response.status_code == 200:
        return response


def fetch_user_info(user_ids):
    """
    fetches email-addresses for users registered in Laji.fi
    :param user_ids: user identifiers
    :returns: a dictionary with user ids as keys and email addresses as values
    """
    username = settings.LAJIPERSONAPI_USER
    password = settings.LAJIPERSONAPI_PW
    result = {}

    missing_user = []
    for user_id in user_ids:
        cache_key = user_id.replace(' ', '_')
        user_info = cache.get('user_info' + cache_key, 'has expired')
        if 'has expired' in user_info:
            if user_id not in missing_user:
                missing_user.append(user_id)
        else:
            result[user_id] = user_info

    start = 0
    limit = 500
    while start < len(missing_user):
        try:
            user_list = '+'.join(missing_user[start:start+limit])
            response = requests.get(
                '{}{}?format=json'.format(settings.LAJIPERSONAPI_URL, user_list),
                auth=HTTPBasicAuth(username, password),
                timeout=settings.SECRET_TIMEOUT_PERIOD
            )
            start += limit
        except requests.exceptions.RequestException:
            response = Container()
            response.status_code = 500

        if response.status_code == 200:
            data = response.json()
            if 'rdf:RDF' in data and 'MA.person' in data['rdf:RDF']:
                all_person_data = data['rdf:RDF']['MA.person']
                if type(all_person_data) is not list:
                    all_person_data = [all_person_data]

                for person_data in all_person_data:
                    user_id = person_data['rdf:about'].split('/')[-1]
                    email = person_data['MA.emailAddress'] if 'MA.emailAddress' in person_data else None
                    name = person_data['MA.fullName'] if 'MA.fullName' in person_data else None

                    user_info = Namespace(email=email, name=name)

                    cache_key = user_id.replace(' ', '_')
                    cache.set('user_info' + cache_key, user_info, timeout=3600)
                    result[user_id] = user_info

    for user_id in missing_user:
        if user_id not in result:
            result[user_id] = Namespace(email=user_id, name=user_id)

    return result


def fetch_email_address(user_id):
    """
    fetches email-address for a person registered in Laji.fi
    :param user_id: person identifier
    :returns: user's email-address
    """
    return fetch_user_info([user_id])[user_id].email


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
    if userRequest.downloadType == Request.API_KEY:
        payload["apiKeyExpires"] = userRequest.apiKeyExpires if userRequest.apiKeyExpires is not None \
            else Request.THREE_MONTHS

    response = requests.post(settings.LAJIAPI_URL+"warehouse/private-query/downloadApproved",
                             data=payload, timeout=settings.SECRET_TIMEOUT_PERIOD)
    return response.ok

def delete_collections_cache():
    caches['database'].delete('collection_update')
    caches['database'].delete('collections')


def get_download_handlers_where_collection(collectionId):
    result = {}
    collections = get_collections()
    for co in collections:
        if co['id'] == collectionId:
            result = co.get('downloadRequestHandler', {})
            break
    return result


def get_contact_email_for_collection(collectionId):
    result = None
    collections = get_collections()
    for co in collections:
        if co['id'] == collectionId:
            result = co.get('contactEmail', None)
            break
    return result


def get_collections_where_download_handler(userId):
    resultlist = []
    collections = get_collections()
    for co in collections:
        if userId in co.get('downloadRequestHandler', {}):
            resultlist.append(co['id'])
    return resultlist


def get_download_handlers_with_collections_listed_for_collections(requestId, collectionsList):
    resultlist = []
    collections = get_collections()
    collections = [co for co in collections if co['id'] in [coli.address for coli in collectionsList]]
    repeatedhandlers = [co.get('downloadRequestHandler', ['None']) for co in collections]
    handlers = set(chain(*repeatedhandlers))
    handlerswithcollections = []
    for ha in handlers:
        handlerswithcollections.append({"handlers": [{"name": ha, "id": ha, "email": 'undefined'}], "collections": [
                                       co for co in collections if ha in co.get('downloadRequestHandler', ['None'])]})

    emailed_handlers = HandlerInRequest.objects.filter(request=requestId)
    for hanco in handlerswithcollections:
        hanco["handlers"][0]["mailed"] = False
        for handler in emailed_handlers:
            if hanco["handlers"][0]["id"] == handler.user:
                if handler.emailed:
                    hanco["handlers"][0]["mailed"] = True
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

    # Groups handlers with identical collections
    while(True):
        grouped = False
        for i in range(0, len(handlerswithcollections)):
            for j in range(i+1, len(handlerswithcollections)):
                if handlerswithcollections[i]['collections'] == handlerswithcollections[j]['collections']:
                    handlerswithcollections[i]["handlers"] = handlerswithcollections[i]["handlers"] + \
                        (handlerswithcollections[j]["handlers"])
                    handlerswithcollections.remove(handlerswithcollections[j])
                    grouped = True
                    break
            if grouped:
                break
        if not grouped:
            break
    return handlerswithcollections


def get_download_handlers_for_collections(collectionsList):
    resultlist = []
    collections = get_collections()
    collections = [co for co in collections if co['id'] in [coli.address for coli in collectionsList]]
    handlers = [co.get('downloadRequestHandler', []) for co in collections]
    return list(set(chain(*handlers)))


def is_collections_missing_download_handler(collectionsList):
    collections = get_collections()
    collections = [co for co in collections if co['id'] in [coli.address for coli in collectionsList]]
    missing = False
    for co in collections:
        if 'None' == co.get('downloadRequestHandler', ['None'])[0]:
            missing = True
            break
    return missing


def is_download_handler(userId):
    return len(get_collections_where_download_handler(userId)) > 0


def is_download_handler_in_collection(userId, collectionId):
    collections = get_collections()
    for co in collections:
        if co['id'] == collectionId:
            if userId in co.get('downloadRequestHandler', {}):
                return True
            else:
                return False
    return False


def get_collection_counts(collection, lang):
    try:
        count_list = json.loads(collection.count_list, object_hook=lambda d: Namespace(**d))
    except JSONDecodeError:
        # for backwards combability
        result = []
        if collection.quarantineSecured > 0:
            result.append(Namespace(
                label=ugettext('secured_by_quarantine'),
                count=collection.quarantineSecured
            ))
        if collection.taxonSecured > 0:
            result.append(Namespace(
                label=ugettext('secured_by_sensitivity'),
                count=collection.taxonSecured
            ))
        if collection.customSecured > 0:
            result.append(Namespace(
                label=ugettext('secured_by_data_provider'),
                count=collection.customSecured
            ))

        return result

    for count in count_list:
        count.label = getattr(count.label, lang, '')
    return count_list


def get_collection_count_sum(collection):
    sum = 0
    counts = get_collection_counts(collection, 'fi')
    for count in counts:
        sum += count.count
    return sum


def show_filters(userRequest, lang):
    '''
    Gathers all the names for the filters if available from Laji.api and reforms them into an usable list object.
    Also contains them in a cache to lessen the laji.api strain.
    :param request: request identifier
    :param userRequest: language code
    '''
    try:
        filterDescriptionList = json.loads(userRequest.filter_description_list, object_hook=lambda d: Namespace(**d))
    except JSONDecodeError:
        return []
    return getattr(filterDescriptionList, lang, [])


def get_filter_link(http_request, userRequest, role):
    lang = http_request.LANGUAGE_CODE

    if role == ADMIN or role == HANDLER_ANY:
        data = userRequest.private_link
    else:
        data = userRequest.public_link

    try:
        parsed_data = json.loads(data, object_hook=lambda d: Namespace(**d))
    except JSONDecodeError:
        return None

    link = getattr(parsed_data, lang, None)
    return update_collection_in_filter_link(link, userRequest)


def update_collection_in_filter_link(link, user_request):
    removed_collections = Collection.objects.filter(request=user_request.id, status=Col_StatusEnum.DISCARDED)
    removed_collection_ids = [c.address for c in removed_collections]

    if len(removed_collection_ids) > 0:
        parsed_link = urlparse(link)
        qs = dict(parse_qs(parsed_link.query))

        if 'collectionId' in qs:
            collection_ids = str(qs['collectionId'][0]).split(',')
            collection_ids = [c for c in collection_ids if c not in removed_collection_ids]
            qs['collectionId'] = [','.join(collection_ids)]

        filtered_collection_ids = []
        if 'collectionIdNot' in qs:
            filtered_collection_ids = str(qs['collectionIdNot'][0]).split(',')
        filtered_collection_ids += removed_collection_ids
        qs['collectionIdNot'] = [','.join(set(filtered_collection_ids))]

        qs = urlencode(qs, True)
        parsed_link = parsed_link._replace(query=qs)
        link = urlunparse(parsed_link)

    return link
