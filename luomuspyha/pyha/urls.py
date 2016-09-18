from django.conf.urls import url

from . import views

app_name = 'pyha'
urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^login/$', views.login, name='login'),
    url(r'^index/$', views.index, name='index'),
]
