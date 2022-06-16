from django.core.management.base import BaseCommand
from pyha.models import Request, StatusEnum, Collection, Col_StatusEnum
from pyha.warehouse import fetch_user_name, get_collection_counts
from pyha.database import get_reasons
from argparse import Namespace
from django.utils.translation import ugettext
from django.conf import settings
import csv
import json
import requests

lang = 'fi'
filtered_fields = ['source', 'changedBy',
                   'downloadFormat', 'downloadIncludes', 'filter_list']
collection_filtered_fields = ['id', 'changedBy', 'downloadRequestHandler',
                              'count', 'taxonSecured', 'customSecured', 'quarantineSecured']
collection_names = {}


class Command(BaseCommand):
    help = 'Generates csv file of requests.'

    # def add_arguments(self, parser):

    def handle(self, *args, **options):
        self.generate_request_data_dump()
        self.generate_collection_data_dump()

    def generate_request_data_dump(self):
        with open('pyha_requests.csv', 'w') as f:
            model_fields = Request._meta.fields + Request._meta.many_to_many
            field_names = [
                field.name for field in model_fields if field.name not in filtered_fields]

            writer = csv.writer(f, delimiter=';')
            writer.writerow(field_names)

            for obj in Request.objects.order_by('date').all():
                row = []

                for field in field_names:
                    value = getattr(obj, field)

                    if field == 'status':
                        status = [a for a in dir(
                            StatusEnum) if not a.startswith('__')]
                        for s in status:
                            if getattr(StatusEnum, s) == value:
                                value = s
                    if field == 'user':
                        value = fetch_user_name(value)
                    if field == 'filter_description_list' or field == 'public_link' or field == 'private_link':
                        value = json.loads(
                            value, object_hook=lambda d: Namespace(**d))
                        value = getattr(value, lang)

                        if field == 'filter_description_list':
                            val = {}
                            for v in value:
                                val[v.label] = v.value
                            value = val
                    if field == 'reason':
                        if value != '':
                            value = {}

                            reasons = json.loads(obj.reason)
                            choices = reasons['argument_choices']
                            fields = reasons['fields']

                            value[ugettext('argument_choices')] = ', '.join(
                                [ugettext(c) for c in choices])
                            for field_name in fields:
                                value[ugettext(field_name)
                                      ] = fields[field_name]

                    row.append(value)

                writer.writerow(row)

    def generate_collection_data_dump(self):
        with open('pyha_request_collections.csv', 'w') as f:
            model_fields = Collection._meta.fields + Collection._meta.many_to_many
            field_names = [
                field.name for field in model_fields if field.name not in collection_filtered_fields + ['request']
            ]
            field_names.insert(0, 'request')
            field_names.insert(2, 'collection_name')

            writer = csv.writer(f, delimiter=';')
            writer.writerow(field_names)

            for obj in Collection.objects.order_by('request').all():
                row = []

                for field in field_names:
                    if field == 'collection_name':
                        value = self.get_collection_name(obj.address)
                    else:
                        value = getattr(obj, field)

                    if field == 'request':
                        value = value.id
                    if field == 'status':
                        status = [a for a in dir(
                            Col_StatusEnum) if not a.startswith('__')]
                        for s in status:
                            if getattr(StatusEnum, s) == value:
                                value = s
                    if field == 'count_list':
                        value = get_collection_counts(obj, lang)
                        val = {}
                        for v in value:
                            val[v.label] = v.count
                        value = val

                    row.append(value)

                writer.writerow(row)

    def get_collection_name(self, address):
        if address not in collection_names:
            collection_names[address] = requests.get(
                settings.LAJIAPI_URL+"collections/"+str(address)+"?access_token="+settings.LAJIAPI_TOKEN+"&lang="+lang, timeout=settings.SECRET_TIMEOUT_PERIOD
            ).json().get('collectionName')

        return collection_names[address]
