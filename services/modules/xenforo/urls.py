from __future__ import unicode_literals
from django.conf.urls import url

from . import views

urlpatterns = [
    # XenForo service control
    url(r'^activate_xenforo/$', views.activate_xenforo_forum, name='auth_activate_xenforo'),
    url(r'^deactivate_xenforo/$', views.deactivate_xenforo_forum, name='auth_deactivate_xenforo'),
    url(r'^reset_xenforo_password/$', views.reset_xenforo_password, name='auth_reset_xenforo_password'),
    url(r'^set_xenforo_password/$', views.set_xenforo_password, name='auth_set_xenforo_password'),
]
