#coding=utf-8
from django.contrib import admin
from django.utils.translation import ugettext_lazy
from django.contrib.admin.models import LogEntry
from simple_history.admin import SimpleHistoryAdmin
# Register your models here.

from pyha.models import Request, Collection, RequestContact, RequestLogEntry, ContactPreset, RequestHandlerChatEntry, RequestInformationChatEntry, RequestSensitiveChatEntry

class Media:
    css = {
         'all': ('static/admin/css/ base.css',)
    }
    
class RequestAdmin(SimpleHistoryAdmin):
    search_fields = ['id', 'lajiId']
class CollectionAdmin(SimpleHistoryAdmin):
    search_fields = ['request__id', 'address']
class RequestContactAdmin(SimpleHistoryAdmin):
    search_fields = ['request__id', 'personName']
class RequestLogEntryAdmin(SimpleHistoryAdmin):
    search_fields = ['request__id', 'collection', 'date', 'user', 'role', 'action']
class ContactPresetAdmin(SimpleHistoryAdmin):
    search_fields = ['user']
class RequestHandlerChatEntryAdmin(SimpleHistoryAdmin):
    search_fields = ['request__id', 'user', 'date', 'target']
class RequestInformationChatEntryAdmin(SimpleHistoryAdmin):
    search_fields = ['request__id', 'user', 'date', 'target']
class RequestSensitiveChatEntryAdmin(SimpleHistoryAdmin):
    search_fields = ['request__id', 'date', 'user']
class LogEntryAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'action_time', 'object_repr', 'action_flag', 'object_id']
    readonly_fields = ('change_message','content_type', 'user', 'action_time', 'object_repr', 'action_flag', 'object_id')
    def has_delete_permission(self, request, obj=None):
        return False
    def has_create_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False
admin.site.register(Request, RequestAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(RequestContact, RequestContactAdmin)
admin.site.register(RequestLogEntry, RequestLogEntryAdmin)
admin.site.register(ContactPreset, ContactPresetAdmin)
admin.site.register(RequestHandlerChatEntry, RequestHandlerChatEntryAdmin)
admin.site.register(RequestInformationChatEntry, RequestInformationChatEntryAdmin)
admin.site.register(RequestSensitiveChatEntry, RequestSensitiveChatEntryAdmin)
admin.site.register(LogEntry, LogEntryAdmin)
admin.site.site_header = ugettext_lazy('Pyha administration')
admin.site.site_title = ugettext_lazy('Pyha admin')