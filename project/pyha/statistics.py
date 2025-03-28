import json

from django.db.models import Count, Sum, Case, When, IntegerField, Q, F
from django.db.models.functions import TruncYear

from pyha.database_utils import get_encoded_term_for_json_field_regex_search
from pyha.decorator import cached
from pyha.models import Request, Collection, Col_StatusEnum, StatusEnum

cache_timeout = 25 * 60 * 60

@cached(cache_timeout, 'database')
def get_request_count_by_year():
    results = (
        _get_base_request_query()
            .annotate(year=TruncYear('date'))
            .values('year')
            .annotate(total_count=Count('id'))
            .values('year', 'total_count')
            .order_by('year')
    )

    return [{'year': value['year'].year, 'total_count': value['total_count']} for value in results]


@cached(cache_timeout, 'database')
def get_collection_request_counts(year=None):
    collections_query = Collection.objects.filter(status__gte=0, request__status__gt=0)
    if year:
        collections_query = collections_query.filter(request__date__year=year)

    return list(
        collections_query
            .values('address')
            .annotate(
                total_count=Count('address'),
                approved_count=_get_count_annotation(status=Col_StatusEnum.APPROVED),
                waiting_count=_get_count_annotation(Q(status=Col_StatusEnum.WAITING) & ~Q(request__status=StatusEnum.WAITING_FOR_INFORMATION)),
                rejected_count=_get_count_annotation(status=Col_StatusEnum.REJECTED),
                waiting_for_information_count=_get_count_annotation(Q(status=Col_StatusEnum.WAITING) & Q(request__status=StatusEnum.WAITING_FOR_INFORMATION))
            )
            .values('total_count', 'approved_count', 'waiting_count', 'rejected_count', 'waiting_for_information_count', id=F('address'))
            .order_by('-total_count')
    )


@cached(cache_timeout, 'database')
def get_request_reason_counts(year=None):
    reasons = [
        'reason_zoning',
        'reason_permission',
        'reason_enviromental',
        'reason_natura',
        'reason_scientific',
        'reason_forest',
        'reason_other'
    ]

    return _get_reason_statistics(reasons, year)


@cached(cache_timeout, 'database')
def get_request_reason_phrase_counts(year=None):
    phrases = [
        'Tuulivoima',
        'Kaava',
        'Voimajohto',
        'Aurinkovoima',
        'Rata',
        'Väylä',
        'Malminetsintä',
        'Liikenne'
    ]

    search_terms = {}

    for phrase in phrases:
        search_terms[phrase] = get_encoded_term_for_json_field_regex_search(phrase)

    annotations = {}
    aggregations = {}

    for phrase in phrases:
        count_key = '{}_count'.format(phrase)
        annotations[count_key] = _get_count_annotation(
            reason__iregex=r'(^|\W)(' + search_terms[phrase] + r')(\W|$)'
        )
        aggregations[phrase] = Sum(count_key)

    requests = (
        _get_base_request_query(year)
            .annotate(**annotations)
            .aggregate(**aggregations)
    )

    return _count_dict_to_sorted_list(requests)


@cached(cache_timeout, 'database')
def get_request_party_involvement_counts(year=None):
    arguments = [
        'argument_only_requester_check',
        'argument_customer_check',
        'argument_other_party_check'
    ]

    return _get_reason_statistics(arguments, year)


def _get_reason_statistics(search_keys, year=None):
    annotations = {}
    aggregations = {}

    for key in search_keys:
        annotations['{}_count'.format(key)] = _get_count_annotation(reason__contains=json.dumps(key))
        aggregations[key] = Sum('{}_count'.format(key))

    results = (
        _get_base_request_query(year)
            .annotate(**annotations)
            .aggregate(**aggregations)
    )

    return _count_dict_to_sorted_list(results)


def _get_base_request_query(year=None):
    base_query = Request.objects.filter(status__gt=0)
    if year:
        base_query = base_query.filter(date__year=year)
    return base_query


def _get_count_annotation(q=None, **kwargs):
    return Count(Case(
    When(q, then=1, **kwargs),
        output_field=IntegerField()
    ))


def _count_dict_to_sorted_list(result_dict):
    result_list = [{'value': key, 'count': count if count is not None else 0} for (key, count) in result_dict.items()]
    result_list.sort(key=lambda x: x['count'], reverse=True)
    return result_list
