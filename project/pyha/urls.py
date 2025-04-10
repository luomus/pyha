from django.conf.urls import url
from django.conf import settings
from django.views.generic import RedirectView
from config.timers import *
from pyha.views import api, api_statistics, api_docs, index, requestform, requestview, logout, ajax, usersettings

app_name = 'pyha'
urlpatterns = [
    url(r'^pyha/?$', index.pyha, name='pyha'),
    url(r'^/?$', index.index, name='root'),
    url(r'^index/?$', index.pyha, name='index'),
    url(r'^login/?$', index.index, name='login'),
    url(r'^groupdeleterequest/?$', index.group_delete_request, name='group_delete_request'),
    url(r'^logout/?$', logout.logout, name='logout'),
    url(r'^settings/?$', usersettings.usersettings, name='usersettings'),
    url(r'^ajax/getCollection/?$', ajax.get_collection_ajax, name='get_collection_ajax'),
    url(r'^ajax/getSummary/?$', ajax.get_summary_ajax, name='get_summary_ajax'),
    url(r'^ajax/createContact/?$', ajax.create_contact_ajax, name='create_contact_ajax'),
    url(r'^ajax/removeCollection/?$', ajax.remove_collection_ajax, name='remove_collection_ajax'),
    url(r'^ajax/getDescription/?$', ajax.get_description_ajax, name='get_description_ajax'),
    url(r'^ajax/setDescription/?$', ajax.set_description_ajax, name='set_description_ajax'),
    url(r'^ajax/getRequestList/?$', index.get_request_list_ajax, name='get_request_list_ajax'),
    url(r'^approve/?$', requestform.approve_terms, name='approve'),
    url(r'^request/[1-9][0-9]*/?$', requestview.show_request, name='show_request'),
    url(r'^description/?$', requestview.change_description, name='change_description'),
    url(r'^answer/?$', requestview.answer, name='answer'),
    url(r'^question/?$', requestview.question, name='question'),
    url(r'^groupanswer/?$', requestview.group_answer, name='group_answer'),
    url(r'^information/?$', requestview.information, name='information'),
    url(r'^chatEntryFileDownload/?$', requestview.chat_entry_file_download, name='chat_entry_file_download'),
    url(r'^commentHandler/?$', requestview.comment_handler, name='comment_handler'),
    url(r'^sendEmail/?$', requestview.send_email, name='send_email'),
    url(r'^initializeDownload/?$', requestview.initialize_download, name='initializeDownload'),
    url(r'^downloadLink/?$', ajax.download_link, name='requestDownload'),
    url(r'^gisDownloadStatus/(?P<download_id>[^/]+)/?$', ajax.gis_download_status, name='gis_download_status'),
    url(r'^apiKey/?$', ajax.get_api_key, name='get_api_key'),
    url(r'^saveUserSettings/?$', usersettings.save_user_settings, name='save_user_settings'),
    url(r'^savePyhaSettings/?$', usersettings.save_pyha_settings, name='save_pyha_settings'),
    url(r'^newpdf/?$', api.new_pdf, name='newpdf'),
    url(r'^api/request/?$', api.receiver, name='receiver'),
    url(r'^api/download/(?P<link>[^/]+)/?$', api.download, name='download'),
    url(r'^api/newcount/?$', api.new_count, name='new_count'),
    url(r'^{0}/?$'.format(settings.SECRET_STATUS_SUB_DIR), api.status, name='status'),
    url(r'^api/swagger.json$', api_docs.api_spec, name='api_spec'),
    url(r'^api/docs/?$', api_docs.api_docs, name='swagger-ui'),
    url(r'^api/statistics/countByYear/?$', api_statistics.request_count_by_year, name='count_by_year'),
    url(r'^api/statistics/collectionCounts/?$', api_statistics.collection_counts, name='collection_counts'),
    url(r'^api/statistics/reasonCounts/?$', api_statistics.request_reason_counts, name='reason_counts'),
    url(r'^api/statistics/reasonPhraseCounts/?$', api_statistics.request_reason_phrase_counts, name='reason_phrase_counts'),
    url(r'^api/statistics/partyInvolvementCounts/?$', api_statistics.request_party_involvement_counts, name='party_involvement_counts'),
    url(r'^role/?$', logout.change_role, name='change_role'),
    url(r'^freezeRequest/?$', requestview.freeze, name='freeze'),
    url(r'^refreshCollectionsCache/?$', requestview.refresh_collections_cache, name='refresh_collections_cache'),
    url(r'^lang/?$', logout.change_lang, name='set_language'),
    url(r'^handler-manual.pdf$', RedirectView.as_view(
        url='https://cdn.laji.fi/files/pyha/Aineistopyyntöjärjestelmä_ohje_käsittelijoille_2022.pdf',
        permanent=False
    ), name='handler_manual')
]
