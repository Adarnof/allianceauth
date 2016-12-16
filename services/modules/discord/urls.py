from __future__ import unicode_literals
from django.conf.urls import url

from . import views

urlpatterns = [
    # Discord Service Control
    url(r'^activate_discord/$', views.activate_discord, name='auth_activate_discord'),
    url(r'^deactivate_discord/$', views.deactivate_discord, name='auth_deactivate_discord'),
    url(r'^reset_discord/$', views.reset_discord, name='auth_reset_discord'),
    url(r'^discord_callback/$', views.discord_callback, name='auth_discord_callback'),
    url(r'^discord_add_bot/$', views.discord_add_bot, name='auth_discord_add_bot'),
]
