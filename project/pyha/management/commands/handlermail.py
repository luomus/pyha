from django.core.management.base import BaseCommand
from pyha.email import send_mail_for_unchecked_requests
from pyha.database import count_unhandled_requests
from django.core.cache import caches

class Command(BaseCommand):
    help = 'Sends reminder emails to all collection handlers for unhandled requests'

    #def add_arguments(self, parser):
    
    def handle(self, *args, **options):
        collections = caches['collections'].get('collections')
        downloadRequestHandlers = set()
        lang = 'fi' #ainakin toistaiseksi
        for co in collections:
            for handler in co.get('downloadRequestHandler', {}):
                downloadRequestHandlers.add(handler)
        for handler in downloadRequestHandlers:
            count = count_unhandled_requests(handler)
            if(count > 0):
                send_mail_for_unchecked_requests(handler, count, lang)