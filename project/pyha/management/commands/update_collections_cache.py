from django.core.management.base import BaseCommand
from pyha.warehouse import update_collections


class Command(BaseCommand):
    help = 'Updates collections cache.'

    # def add_arguments(self, parser):

    def handle(self, *args, **options):
        success = update_collections()
        print('Success: {}'.format(success))