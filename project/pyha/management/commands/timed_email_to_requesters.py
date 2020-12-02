from django.core.management.base import BaseCommand
from pyha.email import send_mail_for_unchecked_requests, send_mail_for_unchecked_requests_to_email
from pyha.database import update_collection_handlers, update_collection_handlers_autom_email_sent_time, get_unhandled_requests_data
from pyha.warehouse import get_contact_email_for_collection
from django.core.cache import caches

class Command(BaseCommand):
    help = 'Sends status update emails to requesters.'

    #def add_arguments(self, parser):

    def handle(self, *args, **options):
        pass
