from django.core.management.base import BaseCommand
from pyha.statistics import get_request_count_by_year, get_collection_request_counts, get_request_reason_counts, get_request_reason_phrase_counts, get_request_party_involvement_counts


class Command(BaseCommand):
    help = 'Updates statistics cache.'

    def handle(self, *args, **options):
        year_counts = get_request_count_by_year(refresh_cache=True)

        years = [value['year'] for value in year_counts]

        for year in [None] + years:
            get_collection_request_counts(refresh_cache=True, year=year)
            get_request_reason_counts(refresh_cache=True, year=year)
            get_request_reason_phrase_counts(refresh_cache=True, year=year)
            get_request_party_involvement_counts(refresh_cache=True, year=year)

        print('Statistics cache updated')
