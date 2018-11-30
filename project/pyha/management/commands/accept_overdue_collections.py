from django.core.management.base import BaseCommand
from pyha.database import get_collections_waiting_atleast_days, is_collection_waiting, update_request_status
from pyha.models import Col_StatusEnum, RequestLogEntry, Request
from pyha.roles import CAT_ADMIN
from pyha.log_utils import changed_by
from time import sleep
from random import randint


        sleep(randint(0, interval))
        if(is_collection_waiting(collection)):
            collection.status = Col_StatusEnum.APPROVED
            collection.changedBy = changed_by("pyha")
            collection.save()
            update_request_status(collection.request.id, collection.request.lang)
        
