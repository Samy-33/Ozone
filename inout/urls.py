from django.conf.urls import url
from django.contrib.auth.views import logout

from .views import (activate, allow, authenticate_user, clogin, code_edit,
                    feedback, give_contests, index, profile, register)

urlpatterns = [
    url(r"^$", clogin, name="login"),
    url(r'^authenticate/$', authenticate_user, name="authenticate-user"),
    url(r"^logout/$", logout, {'next_page': '/'}, name="logout"),
    url(r"^home/$", index, name="home"),
    url(r'^register/$', register, name='register'),
    url(r'^activate/$', activate, name='activate'),
    url(r'^profile/(?P<username>[a-zA-z0-9]{1,15})/$', profile, name='profile'),
    url(r'^code/$', code_edit, name='code'),
    url(r'^profile/[a-zA-Z0-9]+/allowcons/$', give_contests, name='consal'),
    url(r'^profile/[a-zA-Z0-9]+/allow/$', allow, name='allow'),
    url(r'^feedback/$', feedback, name='feedback'),
]
