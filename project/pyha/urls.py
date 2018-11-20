from django.conf.urls import url, include
from django.conf import settings
from pyha.views import api, index, requestform, requestview, logout, ajax

app_name = 'pyha'
urlpatterns = [
    url(r'^pyha/?$', index.pyha, name='pyha'),
    url(r'^/?$', index.index, name='root'),
    url(r'^index/?$', index.pyha, name='index'),
    url(r'^login/?$', index.index, name='login'),
    url(r'^logout/?$', logout.logout, name='logout'),
    url(r'^ajax/getTaxon/?$', ajax.get_taxon_ajax, name='get_taxon_ajax'),
    url(r'^ajax/getCustom/?$', ajax.get_custom_ajax, name='get_custom_ajax'),
    url(r'^ajax/getCollection/?$', ajax.get_collection_ajax, name='get_collection_ajax'),
    url(r'^ajax/getSummary/?$', ajax.get_summary_ajax, name='get_summary_ajax'),
    url(r'^ajax/createContact/?$', ajax.create_contact_ajax, name='create_contact_ajax'),
    url(r'^ajax/removeCollection/?$', ajax.remove_collection_ajax, name='remove_collection_ajax'),
    url(r'^ajax/getDescription/?$', ajax.get_description_ajax, name='get_description_ajax'),
    url(r'^ajax/setDescription/?$', ajax.set_description_ajax, name='set_description_ajax'),    
    url(r'^approve/?$', requestform.approve_terms, name='approve'),
    url(r'^request/[1-9][0-9]*/?$', requestview.show_request, name='show_request'),
    url(r'^description/?$', requestview.change_description, name='change_description'),
    url(r'^answer/?$', requestview.answer, name='answer'),	
    url(r'^information/?$', requestview.information, name='information'),
    url(r'^commentSensitive/?$', requestview.comment_sensitive, name='comment_sensitive'),    
    url(r'^commentHandler/?$', requestview.comment_handler, name='comment_handler'),    
    url(r'^initializeDownload/?$', requestview.initialize_download, name='initializeDownload'),
    url(r'^newpdf/?$', api.new_pdf, name='newpdf'),
    url(r'^api/request/?$', api.receiver, name='receiver'),
    url(r'^api/download/(?P<link>[^/]+)/?$', api.download, name='download'),
    url(r'^api/newcount/?$', api.new_count, name='new_count'),
    url(r'^{0}/?$'.format(settings.SECRET_STATUS_SUB_DIR), api.status, name='status'),
    url(r'^role/?$', logout.change_role, name='change_role'),
    url(r'^freezeRequest/?$', requestview.freeze, name='freeze'),
    url(r'^lang/?$', logout.change_lang, name='set_language'),
]
