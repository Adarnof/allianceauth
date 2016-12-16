from __future__ import unicode_literals
from django.conf.urls import url

from . import views

urlpatterns = [
    # Teamspeak3 service control
    url(r'^activate_teamspeak3/$', views.activate_teamspeak3,
        name='auth_activate_teamspeak3'),
    url(r'^deactivate_teamspeak3/$', views.deactivate_teamspeak3,
        name='auth_deactivate_teamspeak3'),
    url(r'reset_teamspeak3_perm/$', views.reset_teamspeak3_perm,
        name='auth_reset_teamspeak3_perm'),

    # Teamspeak Urls
    url(r'verify_teamspeak3/$', views.verify_teamspeak3, name='auth_verify_teamspeak3'),
]
