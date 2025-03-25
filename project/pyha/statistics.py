import json
import re

from django.db.models import Count, Sum, Case, When, IntegerField, Q, F
from django.db.models.functions import TruncYear

from pyha.database_utils import get_escaped_terms_for_case_insensitive_json_field_search
from pyha.models import Request, Collection, Col_StatusEnum, StatusEnum


def get_request_count_by_year():
    requests = (
        _get_base_request_query()
            .annotate(year=TruncYear('date'))
            .values('year')
            .annotate(total_count=Count('id'))
            .values('year', 'total_count')
            .order_by('year')
    )

    return list(requests)


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


def get_request_reason_counts(year=None):
    reasons = [
        ('reason_zoning', 'landUsePlanning'),
        ('reason_permission', 'permitApplication'),
        ('reason_enviromental', 'environmentalImpactAssessment'),
        ('reason_natura', 'naturaAssessment'),
        ('reason_scientific', 'scientificStudy'),
        ('reason_forest', 'forestPlanning'),
        ('reason_other', 'other')
    ]

    return _get_reason_statistics(reasons, year)


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
        results = get_escaped_terms_for_case_insensitive_json_field_search(phrase)
        search_terms[phrase] = r'|'.join([re.escape(res) for res in results])

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


def get_request_party_involvement_counts(year=None):
    arguments = [
        ('argument_only_requester_check', 'onlyRequester'),
        ('argument_customer_check', 'customer'),
        ('argument_other_party_check', 'otherParty')
    ]

    return _get_reason_statistics(arguments, year)


def _get_reason_statistics(search_keys, year=None):
    annotations = {}
    aggregations = {}

    for (key, label) in search_keys:
        annotations['{}_count'.format(key)] = _get_count_annotation(reason__contains=json.dumps(key))
        aggregations[label] = Sum('{}_count'.format(key))

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
    result_list = [{'value': key, 'count': count} for (key, count) in result_dict.items()]
    result_list.sort(key=lambda x: x['count'], reverse=True)
    return result_list
