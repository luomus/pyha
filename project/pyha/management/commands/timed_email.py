from django.core.management.base import BaseCommand
from pyha.email import send_mail_for_unchecked_requests
from pyha.database import update_collection_handlers_autom_email_sent_time, \
    get_unhandled_requests_data
from pyha.warehouse import get_collections


class Command(BaseCommand):
    help = 'Sends reminder emails to all collection handlers for unhandled requests.'

    # def add_arguments(self, parser):

    def handle(self, *args, **options):
        collections = get_collections()
        download_request_handlers = set()
        for co in collections:
            for handler in co.get('downloadRequestHandler', {}):
                download_request_handlers.add(handler)

        # count_for_contact_email = {}

        for handler in download_request_handlers:
            data = get_unhandled_requests_data(handler)
            if len(data) > 0:
                """
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
                """

                request_ids = [d['request_id'] for d in data]
                send_mail_for_unchecked_requests(handler, request_ids)

        """
        for contact_email in count_for_contact_email:
            send_mail_for_unchecked_requests_to_email(
                contact_email, count_for_contact_email[contact_email]
            )
        """

        update_collection_handlers_autom_email_sent_time()
