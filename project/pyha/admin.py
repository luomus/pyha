#coding=utf-8
from django.contrib import admin
from django.utils.translation import ugettext_lazy
from django.contrib.admin.models import LogEntry
from simple_history.admin import SimpleHistoryAdmin
# Register your models here.

from pyha.models import Request, Collection, HandlerInRequest, RequestContact, RequestLogEntry, ContactPreset, RequestHandlerChatEntry, RequestInformationChatEntry, AdminUserSettings, AdminPyhaSettings, RequestSensitiveChatEntry

class Media:
    css = {
         'all': ('static/admin/css/ base.css',)
    }
    
class RequestAdmin(SimpleHistoryAdmin):
    search_fields = ['id', 'lajiId']
    history_list_display = ["changedBy"]
class CollectionAdmin(SimpleHistoryAdmin):
    search_fields = ['request__id', 'address']
    history_list_display = ["changedBy"]
class RequestContactAdmin(SimpleHistoryAdmin):
    search_fields = ['request__id', 'personName']
    history_list_display = ["changedBy"]
class RequestLogEntryAdmin(SimpleHistoryAdmin):
    search_fields = ['request__id', 'collection', 'date', 'user', 'role', 'action']
    history_list_display = ["changedBy"]
class ContactPresetAdmin(SimpleHistoryAdmin):
    search_fields = ['user']
    history_list_display = ["changedBy"]
class RequestHandlerChatEntryAdmin(SimpleHistoryAdmin):
    search_fields = ['request__id', 'user', 'date', 'target']
    history_list_display = ["changedBy"]
class RequestInformationChatEntryAdmin(SimpleHistoryAdmin):
    search_fields = ['request__id', 'user', 'date', 'target']
    history_list_display = ["changedBy"]
class RequestSensitiveChatEntryAdmin(SimpleHistoryAdmin):
    search_fields = ['request__id', 'date', 'user']
    history_list_display = ["changedBy"]
class AdminUserSettingsAdmin(SimpleHistoryAdmin):
    search_fields = ['user', 'customEmailAddress']
    history_list_display = ["changedBy"]
class AdminPyhaSettingsAdmin(SimpleHistoryAdmin):
    search_fields = ['settingsName']
    history_list_display = ["changedBy"]
class HandlerInRequestAdmin(SimpleHistoryAdmin):
    search_fields = ['user', 'request__id']
    history_list_display = ["changedBy"]
    
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
admin.site.register(HandlerInRequest, HandlerInRequestAdmin)
admin.site.register(RequestContact, RequestContactAdmin)
admin.site.register(RequestLogEntry, RequestLogEntryAdmin)
admin.site.register(ContactPreset, ContactPresetAdmin)
admin.site.register(RequestHandlerChatEntry, RequestHandlerChatEntryAdmin)
admin.site.register(RequestInformationChatEntry, RequestInformationChatEntryAdmin)
admin.site.register(RequestSensitiveChatEntry, RequestSensitiveChatEntryAdmin)
admin.site.register(AdminUserSettings, AdminUserSettingsAdmin)
admin.site.register(AdminPyhaSettings, AdminPyhaSettingsAdmin)
admin.site.register(LogEntry, LogEntryAdmin)
admin.site.site_header = ugettext_lazy('Pyha administration')
admin.site.site_title = ugettext_lazy('Pyha admin')