from django.conf.urls import url, include
from . import views

app_name = 'contests'

urlpatterns = [
	url(r'^$', views.index, name="index"),
	url(r'^create/$', views.create, name="create"),
]