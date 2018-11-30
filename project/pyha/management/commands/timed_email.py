from django.core.management.base import BaseCommand
from pyha.email import send_mail_for_unchecked_requests, send_mail_for_missing_handlers
from pyha.database import count_unhandled_requests, update_collection_handlers
from django.core.cache import caches

class Command(BaseCommand):
    help = 'Sends reminder emails to all collection handlers for unhandled requests. Also sends email for collections missing handlers.'

    #def add_arguments(self, parser):
    
    def handle(self, *args, **options):
        update_collection_handlers()
        collections = caches['collections'].get('collections')
        downloadRequestHandlers = set()
        lang = 'fi' #ainakin toistaiseksi
        collections_missing_handler = []
        for co in collections:
                for handler in co.get('downloadRequestHandler', {}):
                    downloadRequestHandlers.add(handler)
                if(co.get('downloadRequestHandler', {}) == {}):
                        collections_missing_handler.append(co.get('id'))
        for handler in downloadRequestHandlers:
            count = count_unhandled_requests(handler)
            if(count > 0):
                send_mail_for_unchecked_requests(handler, count, lang)
        if(len(collections_missing_handler) > 0):
            send_mail_for_missing_handlers(collections_missing_handler, "fi")