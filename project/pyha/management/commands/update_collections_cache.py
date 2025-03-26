from django.core.management.base import BaseCommand
from pyha.warehouse import get_collections, delete_collections_cache


class Command(BaseCommand):
    help = 'Updates collections cache.'

    # def add_arguments(self, parser):

    def handle(self, *args, **options):
        delete_collections_cache()
        get_collections()
        print('Collections cache updated')
