from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from . import views

app_name = 'inout'

urlpatterns = [
	url(r"^$", views.clogin, name = "login"),
	url(r"logout/", auth_views.logout, {'next_page':'/'}, name="logout"),
	url(r"home/", views.index, name="home"),
	url(r'register/', views.register, name='register'),
	url(r'activate/', views.activate, name='activate'),
	url(r'profyl/', views.profile, name='profile'),
	url(r'contests/', include('contests.urls')),
	url(r'practice', include('practice.urls')),
	url(r'code/', views.code_edit, name='code'),
	url(r'allowcons/', views.give_contests, name='consal'),
	#url(r'', views.)
]
