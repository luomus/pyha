from django.utils import translation
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.translation import gettext as _

from pyha.collection_metadata import get_sub_collections
from pyha.decorator import allowed_methods
from pyha.statistics import get_request_count_by_year, get_collection_request_counts, get_request_reason_counts, \
    get_request_reason_phrase_counts, get_request_party_involvement_counts
from pyha.view_utils import get_non_negative_int_query_param, convert_to_camel_case, paginate, get_query_param, \
    get_all_languages
from pyha.warehouse import get_collections_by_id_and_lang


@allowed_methods(['GET'])
@csrf_exempt
def request_count_by_year(http_request):
    """
      ---
      get:
        description: Get request count by year
        responses:
          200:
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    results:
                      type: array
                      items:
                        type: object
                        properties:
                          year:
                            type: integer
                          totalCount:
                            type: integer
        tags:
          - Statistics
    """
    results = get_request_count_by_year()
    return JsonResponse({'results': convert_to_camel_case(results)})


@allowed_methods(['GET'])
@csrf_exempt
def collection_counts(http_request):
    """
      ---
      get:
        description: Get collection request counts
        parameters:
          - in: query
            name: collection
            description: filter by root collection id
            schema:
              type: string
          - in: query
            name: year
            description: filter by year
            schema:
              type: integer
          - in: query
            name: lang
            description: language
            schema:
              type: string
          - in: query
            name: page
            description: page number
            schema:
              type: string
          - in: query
            name: pageSize
            description: page size
            schema:
              type: integer
        responses:
          200:
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    results:
                      type: array
                      items:
                        type: object
                        properties:
                          totalCount:
                            type: integer
                          approvedCount:
                            type: integer
                          waitingCount:
                            type: integer
                          rejectedCount:
                            type: integer
                          waitingForInformationCount:
                            type: integer
                          id:
                            type: string
                          collectionName:
                            type: string
        tags:
          - Statistics
    """
    root_collection = http_request.GET.get('collection')
    year = get_non_negative_int_query_param(http_request, 'year')
    lang = get_query_param(http_request, 'lang', 'fi', get_all_languages())
    page = get_non_negative_int_query_param(http_request, 'page')
    page_size = get_non_negative_int_query_param(http_request, 'pageSize')

    results = _get_collection_counts(root_collection, year, lang)

    response = {}

    if page is not None and page_size is not None:
        response['currentPage'] = page
        response['pageSize'] = page_size
        response['total'] = len(results)
        results = paginate(results, page, page_size)

    response['results'] = convert_to_camel_case(results)

    return JsonResponse(response)


@allowed_methods(['GET'])
@csrf_exempt
def request_reason_counts(http_request):
    """
      ---
      get:
        description: Get request reason counts
        parameters:
          - in: query
            name: year
            description: filter by year
            schema:
              type: integer
          - in: query
            name: lang
            description: language
            schema:
              type: string
        responses:
          200:
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    results:
                      type: array
                      items:
                        type: object
                        properties:
                          label:
                            type: string
                          count:
                            type: integer
        tags:
          - Statistics
    """
    year = get_non_negative_int_query_param(http_request, 'year')
    lang = get_query_param(http_request, 'lang', 'fi', get_all_languages())

    with translation.override(lang):
        results = get_request_reason_counts(year)
        results_with_label = []

        for result in results:
            results_with_label.append({'label': _(result['value']), 'count': result['count']})

    return JsonResponse({'results': convert_to_camel_case(results_with_label)})


@allowed_methods(['GET'])
@csrf_exempt
def request_reason_phrase_counts(http_request):
    """
      ---
      get:
        description: Get request reason phrase counts
        parameters:
          - in: query
            name: year
            description: filter by year
            schema:
              type: integer
        responses:
          200:
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    results:
                      type: array
                      items:
                        type: object
                        properties:
                          value:
                            type: string
                          count:
                            type: integer
        tags:
          - Statistics
    """
    year = get_non_negative_int_query_param(http_request, 'year')
    results = get_request_reason_phrase_counts(year)
    return JsonResponse({'results': convert_to_camel_case(results)})


@allowed_methods(['GET'])
@csrf_exempt
def request_party_involvement_counts(http_request):
    """
      ---
      get:
        description: Get party involvement counts
        parameters:
          - in: query
            name: year
            description: filter by year
            schema:
              type: integer
          - in: query
            name: lang
            description: language
            schema:
              type: string
        responses:
          200:
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    results:
                      type: array
                      items:
                        type: object
                        properties:
                          label:
                            type: string
                          count:
                            type: integer
        tags:
          - Statistics
    """
    year = get_non_negative_int_query_param(http_request, 'year')
    lang = get_query_param(http_request, 'lang', 'fi', get_all_languages())

    with translation.override(lang):
        results = get_request_party_involvement_counts(year)
        results_with_label = []

        for result in results:
            results_with_label.append({'label': _(result['value']), 'count': result['count']})

    return JsonResponse({'results': convert_to_camel_case(results_with_label)})


def _get_collection_counts(root_collection, year, lang):
    results = get_collection_request_counts(year)

    collection_whitelist = None

    if root_collection is not None:
        collection_whitelist = get_sub_collections(root_collection, True)

    filtered_results = []
    collection_ids = []
    for res in results:
        if collection_whitelist is None or res['id'] in collection_whitelist:
            filtered_results.append(res)
            collection_ids.append(res['id'])

    data_by_id = get_collections_by_id_and_lang(collection_ids, lang)

    for result in filtered_results:
        col_id = result['id']
        result['collectionName'] = data_by_id[col_id]['collectionName'] if col_id in data_by_id else col_id

    return filtered_results
