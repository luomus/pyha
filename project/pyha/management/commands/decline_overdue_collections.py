from django.core.management.base import BaseCommand
from pyha.database import get_collections_waiting_atleast_days, is_collection_waiting_atleast_days, update_request_status
from pyha.models import Col_StatusEnum, RequestLogEntry, Request
from pyha.roles import CAT_HANDLER_COLL
from pyha.log_utils import changed_by
from time import sleep
from random import randint


class Command(BaseCommand):
    help = 'Declines Collections in Requests with Status.WAITING which are overdue by %days% at random times within %interval% seconds.'    
    #def add_arguments(self, parser):

    
    def handle(self, *args, **options):
        days = 28
        interval = 32400
        overdue = list(get_collections_waiting_atleast_days(days))
                
        for collection in overdue:
            collection.performtime = randint(0, interval)
            
        overdue.sort(key=lambda x: x.performtime)
        
        last = 0
        for collection in overdue:
            decline_in_delay(days, collection, collection.performtime - last)
            last = collection.performtime


def decline_in_delay(days, collection, interval):
        sleep(randint(0, interval))
        if(is_collection_waiting_atleast_days(days, collection)):
            collection.status = Col_StatusEnum.REJECTED
            collection.changedBy = changed_by("pyha")
            collection.save()
            RequestLogEntry.requestLog.create(request = Request.objects.get(id = collection.request.id), collection = collection, user = "Laji.fi ICT-team", role = CAT_HANDLER_COLL, action = RequestLogEntry.DECISION_NEGATIVE_OVERDUE)
            userRequest = Request.objects.get(id = collection.request.id)
            update_request_status(userRequest, userRequest.lang)
        