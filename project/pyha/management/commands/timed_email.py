from django.core.management.base import BaseCommand
from pyha.email import send_mail_for_unchecked_requests, send_mail_for_missing_handlers
from pyha.database import count_unhandled_requests, update_collection_handlers, update_collection_handlers_autom_email_sent_time
from django.core.cache import caches
from pyha.models import AdminPyhaSettings

class Command(BaseCommand):
    help = 'Sends reminder emails to all collection handlers for unhandled requests.'

    #def add_arguments(self, parser):
    
    def handle(self, *args, **options):
        settings = AdminPyhaSettings.objects.filter(settingsName = 'default')
        if settings.exists():
            if settings.first().enableDailyHandlerEmail:
                update_collection_handlers()
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
                update_collection_handlers_autom_email_sent_time()