from django.conf.urls import url, include
from . import views

app_name = 'contests'

urlpatterns = [
	url(r'^$', views.index, name="index"),
	url(r'^create/$', views.create, name="create"),
	url(r'^q/(?P<code>[a-zA-z0-9]{4,15})/$', views.contest, name="contest"),
]