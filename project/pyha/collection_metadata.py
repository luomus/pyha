import requests
from django.core.cache import caches, cache

from config import settings


def get_collections():
    return _get_collection_data()['data']


def get_collections_by_id_and_lang(col_ids, lang):
    data_by_id = {}

    missing_collections = []
    for col_id in col_ids:
        value = cache.get(col_id + 'collection_values' + lang, 'has expired')
        if value == 'has expired':
            missing_collections.append(col_id)
        else:
            data_by_id[col_id] = value

    if len(missing_collections) > 0:
        try:
            collections = _fetch_collections_by_id_and_lang(missing_collections, lang)

            for value in collections:
                data_by_id[value['id']] = value
                cache.set(value['id'] + 'collection_values' + lang, value, 7200)
        except:
            pass

    return data_by_id


def get_sub_collections(col_id, include_self=False):
    result = [col_id] if include_self else []

    data = _get_collection_data()
    all_parents = _get_all_parents(col_id, data['parent'])

    tree = data['tree']
    for key in all_parents + [col_id]:
        if key not in tree:
            return result

        tree = tree[key]

    for key, value in _recursive_items(tree):
        result.append(key)

    return result


def _get_collection_data():
    cache_key = 'collection_data'

    if caches['database'].get('collection_update') == 'updated':
        data = caches['database'].get(cache_key)
        if data:
            return data

    try:
        result = _fetch_collections()
    except:
        data = caches['database'].get(cache_key)
        if data:
            return data
        else:
            raise

    tree, parent = _get_collection_id_tree(result)

    data = {'data': result, 'tree': tree, 'parent': parent}

    caches['database'].set(cache_key, data)
    caches['database'].set('collection_update', 'updated', 7200)

    return data


def _get_collection_id_tree(collections):
    parent = {}
    result = {}

    for collection in collections:
        col_id = collection['id']
        parent[col_id] = None
        result[col_id] = {}

    for col in collections:
        if 'isPartOf' in col:
            col_id = col['id']
            col_parent = col['isPartOf']

            if col_parent not in parent:
                continue

            parent[col_id] = col_parent

            all_parents = _get_all_parents(col_id, parent)
            parent_result = _get_nested_value(result, all_parents)
            parent_result[col_id] = result[col_id]
            del result[col_id]

    return result, parent


def _get_all_parents(col_id, parent):
    all_parents = []
    current_parent = parent[col_id] if col_id in parent else None
    while current_parent is not None:
        all_parents = [current_parent] + all_parents
        current_parent = parent[current_parent]
    return all_parents


def _get_nested_value(data, keys):
    for key in keys:
        data = data[key]
    return data


def _recursive_items(dictionary):
    for key, value in dictionary.items():
        if type(value) is dict:
            yield (key, value)
            yield from _recursive_items(value)
        else:
            yield (key, value)


def _fetch_collections():
    payload = {'access_token': settings.LAJIAPI_TOKEN, 'pageSize': 1000, 'page': 1}
    not_finished = True
    result = []

    while not_finished:
        try:
            response = requests.get(
                settings.LAJIAPI_URL+"collections",
                params=payload,
                timeout=settings.SECRET_TIMEOUT_PERIOD
            )
        except:
            raise

        response.raise_for_status()
        data = response.json()

        for co in data['results']:
            if not "MY.metadataStatusHidden" in co.get('MY.metadataStatus', {}):
                result.append(co)

        if payload['page'] < data['lastPage']:
            payload['page'] += 1
        else:
            not_finished = False

    return result


def _fetch_collections_by_id_and_lang(ids, lang):
    results = []

    start_index = 0
    page_size = 100

    while start_index < len(ids):
        ids_part = ids[start_index:start_index + page_size]

        response = requests.get('{}collections'.format(settings.LAJIAPI_URL), {
            'idIn': ','.join(ids_part),
            'lang': lang,
            'access_token': settings.LAJIAPI_TOKEN,
            'pageSize': len(ids)
        }, timeout=settings.SECRET_TIMEOUT_PERIOD)

        response.raise_for_status()

        results += response.json()['results']

        start_index += page_size

    return results
