from django.core.management.base import BaseCommand
from pyha.email import send_mail_for_unchecked_requests, send_mail_for_unchecked_requests_to_email
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

        count_for_contact_email = {}

        for handler in downloadRequestHandlers:
            data = get_unhandled_requests_data(handler)
            if(len(data) > 0):
                for request in data:
                    contact_emails = set()
                    for co in request['collections']:
                        contact_email = get_contact_email_for_collection(co)
                        if contact_email is not None and len(contact_email) > 0:
                            contact_emails.add(contact_email)

                    for contact_email in contact_emails:
                        if contact_email not in count_for_contact_email:
                            count_for_contact_email[contact_email] = 0
                        count_for_contact_email[contact_email] += 1

                send_mail_for_unchecked_requests(handler, len(data), lang)

        for contact_email in count_for_contact_email:
            send_mail_for_unchecked_requests_to_email(
                contact_email, count_for_contact_email[contact_email], lang
            )

        update_collection_handlers_autom_email_sent_time()
