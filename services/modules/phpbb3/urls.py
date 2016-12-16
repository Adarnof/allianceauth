from __future__ import unicode_literals
from django.conf.urls import url

from . import views

urlpatterns = [
    # Forum Service Control
    url(r'^activate_forum/$', views.activate_forum, name='auth_activate_phpbb3'),
    url(r'^deactivate_forum/$', views.deactivate_forum, name='auth_deactivate_phpbb3'),
    url(r'^reset_forum_password/$', views.reset_forum_password, name='auth_reset_phpbb3_password'),
    url(r'^set_forum_password/$', views.set_forum_password, name='auth_set_phpbb3_password'),
]
