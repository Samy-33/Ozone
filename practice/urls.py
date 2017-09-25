from django.conf.urls import url

from practice import views

app_name = 'practice'


urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^(?P<code>[A-Za-z\-]{2,15})/$', views.get_tag, name='gettag'),
]
