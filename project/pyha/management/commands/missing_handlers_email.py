from django.core.management.base import BaseCommand
from pyha.email import send_mail_for_missing_handlers
from pyha.database import update_collection_handlers
from django.core.cache import caches


class Command(BaseCommand):
    help = 'Sends email to ICT for collections missing handlers.'

    # def add_arguments(self, parser):

    def handle(self, *args, **options):
        update_collection_handlers()
        collections = caches['collections'].get('collections')
        collections_missing_handler = []
        for co in collections:
            if(co.get('downloadRequestHandler', {}) == {}):
                collections_missing_handler.append(co.get('id'))
        if(len(collections_missing_handler) > 0):
            send_mail_for_missing_handlers(collections_missing_handler)
