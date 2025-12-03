import json
from django.core.management.base import BaseCommand
import csv
from django.utils.translation import ugettext

from pyha.models import Request


class Command(BaseCommand):
    help = 'Adds data from pyha to general download statistics'

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=str)
        parser.add_argument('output_file', type=str)
        parser.add_argument('--delimiter', type=str, required=False, default=',')
        parser.add_argument('--encoding', type=str, required=False, default='utf-8')

    def handle(self, *args, **options):
        input_file_path = options['input_file']
        output_file_path = options['output_file']
        delimiter = options['delimiter']
        encoding = options['encoding']

        ids = []
        data = []
        index_by_id = {}

        with open(input_file_path, 'r', encoding=encoding) as f:
            reader = csv.reader(f, delimiter=delimiter, )

            i = 0
            for row in reader:
                ids.append(row[0])
                data.append({
                    'id': row[0],
                    'type': row[1],
                    'date': row[2],
                    'email': row[3],
                    'papreason': row[4]
                })
                index_by_id[row[0]] = i
                i += 1

        requests = Request.objects.filter(lajiId__in=ids)
        for obj in requests.all():
            data_item = data[index_by_id[obj.lajiId]]
            data_item['organization'] = obj.personOrganizationName

            reasons = json.loads(obj.reason)
            choices = [ugettext(reason) for reason in reasons['argument_choices']]
            data_item['reason'] = choices

        with open(output_file_path, 'w', encoding=encoding) as f:
            writer = csv.writer(f, delimiter=delimiter)

            for row in data:
                organization = row['organization'] if 'organization' in row else ''
                reason = ', '.join(row['reason']) if 'reason' in row else ''
                writer.writerow(
                    [row['id'], row['type'], row['date'], row['email'], row['papreason'], organization, reason]
                )
