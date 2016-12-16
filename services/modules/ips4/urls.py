from __future__ import unicode_literals
from django.conf.urls import url

from . import views

urlpatterns = [
    # IPS4 Service Control
    url(r'^activate_ips4/$', views.activate_ips4, name='auth_activate_ips4'),
    url(r'^deactivate_ips4/$', views.deactivate_ips4, name='auth_deactivate_ips4'),
    url(r'^reset_ips4_password/$', views.reset_ips4_password, name='auth_reset_ips4_password'),
    url(r'^set_ips4_password/$', views.set_ips4_password, name='auth_set_ips4_password'),
]
