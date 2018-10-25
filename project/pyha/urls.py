from django.conf.urls import url

from pyha.views import api, index, requestform, requestview, logout, ajax

app_name = 'pyha'
urlpatterns = [
    url(r'^/?$', index.index, name='root'),
    url(r'^index/?$', index.index, name='index'),
    url(r'^login/?$', index.index, name='login'),
    url(r'^logout/?$', logout.logout, name='logout'),
    url(r'^ajax/getTaxon/?$', ajax.get_taxon_ajax, name='get_taxon_ajax'),
    url(r'^ajax/getCustom/?$', ajax.get_custom_ajax, name='get_custom_ajax'),
    url(r'^ajax/getCollection/?$', ajax.get_collection_ajax, name='get_collection_ajax'),
    url(r'^ajax/getSummary/?$', ajax.get_summary_ajax, name='get_summary_ajax'),
    url(r'^ajax/createContact/?$', ajax.create_contact_ajax, name='create_contact_ajax'),
    url(r'^ajax/removeCollection/?$', ajax.remove_collection_ajax, name='remove_collection_ajax'),
    url(r'^ajax/getDescription/?$', ajax.get_request_header_ajax, name='get_request_header_ajax'),
    url(r'^ajax/setDescription/?$', ajax.change_description_ajax, name='description_ajax'),    
    url(r'^approve/?$', requestform.approve, name='approve'),
    url(r'^request/[1-9][0-9]*/?$', requestview.show_request),
    url(r'^description/?$', requestview.change_description, name='change_description'),
    url(r'^answer/?$', requestview.answer, name='answer'),	
    url(r'^information/?$', requestview.information, name='information'),
    url(r'^commentSensitive/?$', requestview.comment_sensitive, name='comment_sensitive'),    
    url(r'^initializeDownload/?$', requestview.initialize_download, name='initializeDownload'),
    url(r'^newpdf/?$', api.new_pdf, name='newpdf'),
    url(r'^api/request/?$', api.receiver, name='receiver'),
    url(r'^api/download/(?P<link>[^/]+)/?$', api.download, name='download'),
    url(r'^api/newcount/?$', api.new_count, name='new_count'),
    url(r'^role/?$', logout.change_role, name='change_role')
]
