from django.core.management.base import BaseCommand
from pyha.email import send_status_mail_to_requester
from pyha.database import get_all_waiting_requests, get_collection_status_counts
from django.core.cache import caches

class Command(BaseCommand):
    help = 'Sends status update emails to requesters.'

    #def add_arguments(self, parser):

    def handle(self, *args, **options):
        status = caches['collections'].get('last_timed_email_sent_for_status', {})
        new_status = {}

        requests = get_all_waiting_requests()
        for request in requests:
            accepted, declined, pending = get_collection_status_counts(request.id)
            if accepted > 0 or declined > 0:
                if (
                    request.id not in status or
                    status[request.id]['accepted'] != accepted or
                    status[request.id]['declined'] != declined
                ):
                    send_status_mail_to_requester(request.id, accepted, declined, pending, request.lang)
                    new_status[request.id] = {
                        'accepted': accepted,
                        'declined': declined,
                        'pending': pending
                    }

        caches['collections'].set('last_timed_email_sent_for_status', new_status, timeout=None)
