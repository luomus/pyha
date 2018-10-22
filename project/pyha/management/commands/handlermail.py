from django.core.management.base import BaseCommand, CommandError
from pyha.email import send_mail_for_unchecked_requests
from pyha.models import Request, Collection, RequestLogEntry
from pyha.warehouse import get_collections_where_download_handler
from django.core.cache import caches
from django.conf import settings
import requests
from requests.auth import HTTPBasicAuth

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
            count = 0
            request_list = Request.requests.exclude(status__lte=0).filter(id__in=Collection.objects.filter(address__in = get_collections_where_download_handler(handler), status__gt = 0).values("request"))
            #Ei pysty toteuttamaan sens pyyntöjen laskentaa ilman uutta tapaa selvittää sensitiivinen käsittelijä jostain lajin rajapinnasta
            #if HANDLER_SENS in request.session.get("user_roles", [None]):
                #request_list += Request.requests.all().exclude(status__lte=0)
            for r in request_list:
                if(RequestLogEntry.requestLog.filter(request = r.id, user = handler, action = 'VIEW').count() == 0):
                    count += 1
            if(count > 0):
                send_mail_for_unchecked_requests(handler, count, lang)