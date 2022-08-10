from datetime import datetime
from django.core.management.base import BaseCommand
from pyha.warehouse import send_download_request
from pyha.database import get_failed_download_requests


class Command(BaseCommand):
    help = 'Tries to resend failed download requests.'

    # def add_arguments(self, parser):

    def handle(self, *args, **options):
        failed_requests = get_failed_download_requests()
        for failed_request in failed_requests:
            success = send_download_request(failed_request.request.id)

            if success:
                failed_request.delete()
            else:
                failed_request.date = datetime.now()
                failed_request.nbr_of_tries += 1
                failed_request.save()
