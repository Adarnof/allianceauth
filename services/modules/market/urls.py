from __future__ import unicode_literals
from django.conf.urls import url

from . import views

urlpatterns = [
    # Alliance Market Control
    url(r'^activate_market/$', views.activate_market, name='auth_activate_market'),
    url(r'^deactivate_market/$', views.deactivate_market, name='auth_deactivate_market'),
    url(r'^reset_market_password/$', views.reset_market_password, name='auth_reset_market_password'),
    url(r'^set_market_password/$', views.set_market_password, name='auth_set_market_password'),
]
