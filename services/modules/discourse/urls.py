from __future__ import unicode_literals
from django.conf.urls import url

from . import views

urlpatterns = [
    # Discourse Service Control
    url(r'^discourse_sso$', views.discourse_sso, name='auth_discourse_sso'),
]
