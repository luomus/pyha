from django.core.management.base import BaseCommand
from pyha.email import send_mail_for_unchecked_requests, send_mail_for_missing_handlers
from pyha.database import count_unhandled_requests, update_collection_handlers
from django.core.cache import caches
from pyha.models import AdminPyhaSettings

class Command(BaseCommand):
    help = 'Sends email to ICT for collections missing handlers.'

    #def add_arguments(self, parser):
    
    def handle(self, *args, **options):
        settings = AdminPyhaSettings.objects.filter(settingsName = 'default')
        if settings.exists():
            if settings.first().enableWeeklyMissingHandlersEmail:
                update_collection_handlers()
                collections = caches['collections'].get('collections')
                lang = 'fi' #ainakin toistaiseksi
                collections_missing_handler = []
                for co in collections:
                    if(co.get('downloadRequestHandler', {}) == {}):
                            collections_missing_handler.append(co.get('id'))
                if(len(collections_missing_handler) > 0):
                    send_mail_for_missing_handlers(collections_missing_handler, lang)