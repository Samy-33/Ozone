from django.conf.urls import url, include
from . import views

app_name = 'contests'

urlpatterns = [
	url(r'^$', views.index, name="index"),
	url(r'^create/$', views.create, name="create"),
	url(r'^q/(?P<code>[a-zA-Z0-9]{4,15})/$', views.contest, name="contest"),
	url(r'^q/edit/(?P<code>[a-zA-Z0-9]{4,15})/$', views.editc, name="editc"),
	url(r'^q/edit/(?P<code>[a-zA-Z0-9]{4,15})/p/(?P<question>[a-zA-Z0-9]{3,15})/$', views.editq, name="editq"),
	url(r'^q/(?P<code>[a-zA-Z0-9]{4,15})/p/(?P<question>[a-zA-Z0-9]{3,15})/$', views.problem, name="problem"),
	url(r'^q/edit/(?P<code>[a-zA-Z0-9]{4,15})/a/$', views.addq, name="problem_add"),
	url(r'^q/submit/(?P<code>[a-zA-Z0-9]{3,15})/$', views.submit, name="submit"),
	url(r'^q/delete/(?P<code>[a-zA-Z0-9]{3,15})/$', views.deleteq, name="deleteq"),

]