from django.conf.urls import url, include
from . import views
from inout.views import update
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
    url(r'^q/(?P<contest>[a-zA-Z0-9]{4,15})/rankings/$', views.rankings, name="rankings"),
    url(r'^q/(?P<contest>[a-zA-Z0-9]{4,15})/delete/$', views.deletec, name="deletec"),
    url(r'^q/(?P<contest>[a-zA-Z0-9]{4,15})/boardc/$', views.boardC, name="boardC"),
    url(r'^q/(?P<code>[a-zA-Z0-9]{3,15})/boardq/$', views.boardQ, name="boardQ"),
    url(r'^q/(?P<question>[a-zA-Z0-9]{3,15})/board/(?P<pk>[0-9]+)/problem/$', views.convQ, name="convQ"),
    url(r'^q/(?P<code>[a-zA-Z0-9]{4,15})/board/(?P<pk>[0-9]+)/contest/$', views.convC, name="convC"),
    url(r'^q/(?P<code>[a-zA-Z0-9]{4,15})/update/$', update, name="update"),
    url(r'^q/(?P<code>[a-zA-Z0-9]{4,15})/time/', views.get_time, name='get_time')
]