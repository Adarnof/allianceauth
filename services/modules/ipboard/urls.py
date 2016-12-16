from __future__ import unicode_literals
from django.conf.urls import url

from . import views

urlpatterns = [
    # Ipboard service control
    url(r'^activate_ipboard/$', views.activate_ipboard_forum, name='auth_activate_ipboard'),
    url(r'^deactivate_ipboard/$', views.deactivate_ipboard_forum, name='auth_deactivate_ipboard'),
    url(r'^reset_ipboard_password/$', views.reset_ipboard_password, name='auth_reset_ipboard_password'),
    url(r'^set_ipboard_password/$', views.set_ipboard_password, name='auth_set_ipboard_password'),
]
