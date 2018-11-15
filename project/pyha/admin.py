#coding=utf-8
from django.contrib import admin
from django.utils.translation import ugettext_lazy
from simple_history.admin import SimpleHistoryAdmin
# Register your models here.

from pyha.models import Request, Collection, RequestContact, RequestLogEntry, ContactPreset, RequestHandlerChatEntry, RequestInformationChatEntry, RequestSensitiveChatEntry

class Media:
    css = {
         'all': ('static/admin/css/ base.css',)
    }

admin.site.register(Request, SimpleHistoryAdmin)
admin.site.register(Collection, SimpleHistoryAdmin)
admin.site.register(RequestContact, SimpleHistoryAdmin)
admin.site.register(RequestLogEntry, SimpleHistoryAdmin)
admin.site.register(ContactPreset, SimpleHistoryAdmin)
admin.site.register(RequestHandlerChatEntry, SimpleHistoryAdmin)
admin.site.register(RequestInformationChatEntry, SimpleHistoryAdmin)
admin.site.register(RequestSensitiveChatEntry, SimpleHistoryAdmin)

admin.site.site_header = ugettext_lazy('Welcome adventurer to the Den of Evil beneath Pyha')
admin.site.site_title = ugettext_lazy('Pyha admin')