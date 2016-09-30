from django.conf.urls import url

from . import views

app_name = 'pyha'
urlpatterns = [
    url(r'^/?$', views.index, name='index'),
    url(r'^login/?$', views.login, name='login'),
    url(r'^logout/?$', views.logout, name='logout'),
    url(r'^index/?$', views.index, name='index'),
    url(r'^api/request/?$', views.receiver, name='receiver'),
    url(r'^mock/jsonmock/?$', views.jsonmock, name='jsonmock'),
    url(r'^request/[1-9][0-9]*/?$', views.show_request, name='show_request'),
]
