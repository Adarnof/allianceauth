from __future__ import unicode_literals
from django.conf.urls import url

from . import views

urlpatterns = [
    # SMF Service Control
    url(r'^activate_smf/$', views.activate_smf, name='auth_activate_smf'),
    url(r'^deactivate_smf/$', views.deactivate_smf, name='auth_deactivate_smf'),
    url(r'^reset_smf_password/$', views.reset_smf_password, name='auth_reset_smf_password'),
    url(r'^set_smf_password/$', views.set_smf_password, name='auth_set_smf_password'),
]
