from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from pyha.statistics import get_request_count_by_year, get_collection_request_counts, get_request_reason_counts, \
    get_request_reason_phrase_counts, get_request_party_involvement_counts
from pyha.view_utils import get_int_query_param, convert_to_camel_case
from pyha.warehouse import get_collections_by_id_and_lang


@csrf_exempt
def request_count_by_year(http_request):
    results = get_request_count_by_year()
    return JsonResponse({'results': convert_to_camel_case(results)})


@csrf_exempt
def collection_counts(http_request):
    year = get_int_query_param(http_request, 'year')
    lang = http_request.GET.get('lang')

    results = get_collection_request_counts(year)

    collection_ids = [res['id'] for res in results]
    data_by_id = get_collections_by_id_and_lang(collection_ids, lang)

    for result in results:
        col_id = result['id']
        result['collectionName'] = data_by_id[col_id]['collectionName'] if col_id in data_by_id else col_id

    return JsonResponse({'results': convert_to_camel_case(results)})


@csrf_exempt
def request_reason_counts(http_request):
    year = get_int_query_param(http_request, 'year')
    results = get_request_reason_counts(year)
    return JsonResponse({'results': convert_to_camel_case(results)})


@csrf_exempt
def request_reason_phrase_counts(http_request):
    year = get_int_query_param(http_request, 'year')
    results = get_request_reason_phrase_counts(year)
    return JsonResponse({'results': convert_to_camel_case(results)})


@csrf_exempt
def request_party_involvement_counts(http_request):
    year = get_int_query_param(http_request, 'year')
    results = get_request_party_involvement_counts(year)
    return JsonResponse({'results': convert_to_camel_case(results)})
