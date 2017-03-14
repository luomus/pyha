from django.conf.urls import url

from . import views

app_name = 'pyha'
urlpatterns = [
    url(r'^/?$', views.index, name='index'),
    url(r'^login/?$', views.index, name='login'),
    url(r'^logout/?$', views.logout, name='logout'),
    url(r'^index/?$', views.index, name='index'),
    url(r'^getTaxon/?$', views.get_taxon, name='get_taxon'),
    url(r'^getCustom/?$', views.get_custom, name='get_custom'),
    url(r'^getDescription/?$', views.get_request_header, name='get_request_header'),
    url(r'^getSummary/?$', views.get_summary, name='get_summary'),
    url(r'^createContact/?$', views.create_contact, name='create_contact'),
	url(r'^createContactModal/?$', views.create_contact_modal, name='create_contact_modal'),
    url(r'^index/?$', views.index, name='index'),
    url(r'^api/request/?$', views.receiver, name='receiver'),
    url(r'^api/download/(?P<link>[^/]+)/?$', views.download, name='download'),
	url(r'^api/newcount', views.new_count, name='new_count'),
    url(r'^request/[1-9][0-9]*/?$', views.show_request),
    url(r'^description/?$', views.change_description, name='description'),
    url(r'^removeSens/?$', views.remove_sensitive_data, name='removeSens'),
    url(r'^removeCustom/?$', views.remove_custom_data, name='removeCustom'),
    url(r'^removeAjax/?$', views.remove_ajax, name='removeAjax'),
    url(r'^role/?$', views.change_role, name='change_role'),
    url(r'^approve/?$', views.approve, name='approve'),
    url(r'^answer/?$', views.answer, name='answer'),
	url(r'^newpdf/?$', views.new_pdf, name='newpdf'),
    url(r'^information/?$', views.information, name='information'),
    url(r'^commentSensitive/?$', views.comment_sensitive, name='comment_sensitive'),
    url(r'^removeCollection/?$', views.removeCollection, name='removeCollection'),
    url(r'^initializeDownload/?$', views.initialize_download, name='initializeDownload')
]
