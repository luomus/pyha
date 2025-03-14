from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from pyha.statistics import get_request_count_by_year, get_collection_request_counts, get_request_reason_counts, \
    get_request_reason_phrase_counts, get_request_party_involvement_counts
from pyha.view_utils import get_int_query_param, convert_to_camel_case


@csrf_exempt
def request_count_by_year(http_request):
    result = get_request_count_by_year()
    return JsonResponse({'results': convert_to_camel_case(result)})


@csrf_exempt
def collection_counts(http_request):
    year = get_int_query_param(http_request, 'year')
    result = get_collection_request_counts(year)
    return JsonResponse({'results': convert_to_camel_case(result)})


@csrf_exempt
def request_reason_counts(http_request):
    year = get_int_query_param(http_request, 'year')
    result = get_request_reason_counts(year)
    return JsonResponse({'results': convert_to_camel_case(result)})


@csrf_exempt
def request_reason_phrase_counts(http_request):
    year = get_int_query_param(http_request, 'year')
    result = get_request_reason_phrase_counts(year)
    return JsonResponse({'results': convert_to_camel_case(result)})


@csrf_exempt
def request_party_involvement_counts(http_request):
    year = get_int_query_param(http_request, 'year')
    result = get_request_party_involvement_counts(year)
    return JsonResponse({'results': convert_to_camel_case(result)})
