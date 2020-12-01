from django.core.management.base import BaseCommand
from pyha.email import send_mail_for_unchecked_requests
from pyha.database import update_collection_handlers, update_collection_handlers_autom_email_sent_time, get_unhandled_requests_data
from pyha.warehouse import get_contact_email_for_collection
from django.core.cache import caches

class Command(BaseCommand):
    help = 'Sends reminder emails to all collection handlers for unhandled requests.'

    #def add_arguments(self, parser):

    def handle(self, *args, **options):
        update_collection_handlers()
        collections = caches['collections'].get('collections')
        downloadRequestHandlers = set()
        lang = 'fi' #ainakin toistaiseksi
        for co in collections:
                for handler in co.get('downloadRequestHandler', {}):
                    downloadRequestHandlers.add(handler)

        unhandled_collections = set()

        for handler in downloadRequestHandlers:
            data = get_unhandled_requests_data(handler)
            if(len(data) > 0):
                for request in data:
                    for co in request['collections']:
                        unhandled_collections.add(co)

                send_mail_for_unchecked_requests(handler, count, lang)

        contact_emails = set()

        for co in unhandled_collections:
            contact_email = get_contact_email_for_collection(co)
            if contact_email is not None and len(contact_email) > 0:
                contact_emails.add(contact_email)

        for contact_email in contact_emails:
            pass

        update_collection_handlers_autom_email_sent_time()
