from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'inout'

urlpatterns = [
	url(r"^$", views.clogin, name = "login"),
	url(r"logout/$", auth_views.logout, {'next_page':'/'}, name="logout"),
	url(r"home/$", views.index, name="home"),
	url(r'register/$', views.register, name='register'),
	url(r'activate/$', views.activate, name='activate'),
	url(r'profile/(?P<username>[a-zA-z0-9]{1,15})/$', views.profile, name='profile'),
	url(r'code/$', views.code_edit, name='code'),
	url(r'profile/[a-zA-Z0-9]+/allowcons/$', views.give_contests, name='consal'),
	url(r'profile/[a-zA-Z0-9]+/allow/$', views.allow, name='allow'),
	url(r'not_activated/$', views.not_activated, name='not_activated'),
]

#urlpatterns += 	patterns()