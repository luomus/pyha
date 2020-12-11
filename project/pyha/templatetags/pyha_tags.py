from django import template
from django.utils.translation import gettext
from pyha.models import Col_StatusEnum, StatusEnum
from pyha.roles import USER, HANDLER_ANY, ADMIN

register = template.Library()

@register.filter(name='replaceCommaWithSpace')
def replaceCommaWithSpace(text):
    return text.replace(',', ' ')

@register.simple_tag(name='translateCollectionStatus')
def translateCollectionStatus(status, role, collection_id, handles):
    if status == Col_StatusEnum.WAITING:
        if role == HANDLER_ANY:
            if collection_id in handles:
                return gettext('handler_waiting_for_you')
            else:
                return gettext('handler_waiting_for_others')
        else:
            return gettext('waiting_for_data_provider')
    elif status == Col_StatusEnum.REJECTED:
        return gettext('denied')
    elif status == Col_StatusEnum.APPROVED:
        return gettext('accepted')
    else:
        return gettext('unknown')

@register.simple_tag(name='translateRequestStatus')
def translateRequestStatus(status, role, answerstatus, waitingstatus, downloadable):
    if status == StatusEnum.APPROVETERMS_WAIT:
        return gettext('you_have_not_accepted_terms')
    elif status == StatusEnum.WAITING:
        if role == HANDLER_ANY:
            if answerstatus == 1:
                return gettext('handler_waiting_for_response_on_answer')
            elif waitingstatus == 1:
                return gettext('handler_waiting_for_you')
            else:
                return gettext('handler_waiting_for_others')
        else:
            return gettext('waiting_for_data_provider')
    elif status == StatusEnum.PARTIALLY_APPROVED:
        return gettext('partially_accepted')
    elif status == StatusEnum.REJECTED:
        return gettext('denied')
    elif status == StatusEnum.APPROVED:
        return gettext('accepted')
    elif status == StatusEnum.WAITING_FOR_INFORMATION:
        return gettext('waiting_for_additional_information')
    elif status == StatusEnum.WAITING_FOR_DOWNLOAD:
        return gettext('waiting_for_download')
    elif status == StatusEnum.DOWNLOADABLE:
        if downloadable:
            return gettext('ready_for_download')
        else:
            return gettext('download_has_expired')
    elif status == StatusEnum.WITHDRAWN:
         return gettext('withdrawn')
    else:
        return gettext('unknown')
