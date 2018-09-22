from django.conf.urls import url

from pyha.views import api, index, requestform, requestview, logout, skipofficial

app_name = 'pyha'
urlpatterns = [
    url(r'^/?$', index.index, name='index'),
    url(r'^index/?$', index.index, name='index'),
    url(r'^login/?$', index.index, name='login'),
    url(r'^logout/?$', logout.logout, name='logout'),
    url(r'^getTaxon/?$', requestform.get_taxon, name='get_taxon'),
    url(r'^getCustom/?$', requestform.get_custom, name='get_custom'),
    url(r'^getCollection/?$', requestform.get_collection, name='get_collection'),
    url(r'^getSummary/?$', requestform.get_summary, name='get_summary'),
    url(r'^createContact/?$', requestform.create_contact_ajax, name='create_contact_ajax'),
    url(r'^removeSens/?$', requestform.remove_sensitive_data, name='removeSens'),
    url(r'^removeCustom/?$', requestform.remove_custom_data, name='removeCustom'),
    url(r'^removeAjax/?$', requestform.remove_ajax, name='removeAjax'),
    url(r'^removeCollection/?$', requestform.removeCollection, name='removeCollection'),
    url(r'^approve/?$', requestform.approve, name='approve'),
    url(r'^getDescription/?$', requestview.get_request_header, name='get_request_header'),
    url(r'^request/[1-9][0-9]*/?$', requestview.show_request),
    url(r'^description/?$', requestview.change_description, name='description'),
	url(r'^descriptionajax/?$', requestview.change_description_ajax, name='description_ajax'),    
    url(r'^answer/?$', requestview.answer, name='answer'),	
    url(r'^information/?$', requestview.information, name='information'),
    url(r'^commentSensitive/?$', requestview.comment_sensitive, name='comment_sensitive'),    
    url(r'^initializeDownload/?$', requestview.initialize_download, name='initializeDownload'),
    url(r'^newpdf/?$', api.new_pdf, name='newpdf'),
    url(r'^api/request/?$', api.receiver, name='receiver'),
    url(r'^api/download/(?P<link>[^/]+)/?$', api.download, name='download'),
    url(r'^api/newcount/?$', api.new_count, name='new_count'),
    url(r'^role/?$', logout.change_role, name='change_role'),
    url(r'^approval/?$', skipofficial.requestform.approve, name='approval')
]
