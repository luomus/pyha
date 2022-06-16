from django.core.management.base import BaseCommand
from pyha.email import send_status_mail_to_requester
from pyha.database import get_all_waiting_requests, get_collection_status_counts, get_latest_request_sent_status_email, save_request_sent_status_email


class Command(BaseCommand):
    help = 'Sends status update emails to requesters.'

    # def add_arguments(self, parser):

    def handle(self, *args, **options):
        new_status = {}

        requests = get_all_waiting_requests()
        for request in requests:
            last_email = get_latest_request_sent_status_email(request.id)
            accepted, declined, pending = get_collection_status_counts(request.id)
            if accepted > 0 or declined > 0:
                if (
                    last_email is None or
                    last_email.accepted_count != accepted or
                    last_email.declined_count != declined
                ):
                    send_status_mail_to_requester(request.id, accepted, declined, pending, request.lang)
                    save_request_sent_status_email(request, accepted, declined, pending)
