from __future__ import unicode_literals
from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import ugettext_lazy as _

from . import views

urlpatterns = [
    # Jabber Service Control
    url(r'^activate_jabber/$', views.activate_jabber, name='auth_activate_openfire'),
    url(r'^deactivate_jabber/$', views.deactivate_jabber, name='auth_deactivate_openfire'),
    url(r'^reset_jabber_password/$', views.reset_jabber_password, name='auth_reset_openfire_password'),
]

urlpatterns += i18n_patterns(
    # Jabber Broadcast
    # TODO: Add menu hook so that NoReverseMatch isnt thrown when jabber/mumble is disabled
    url(_(r'^services/jabber_broadcast/$'), views.jabber_broadcast_view, name='auth_jabber_broadcast_view'),
    # Jabber
    url(_(r'^set_jabber_password/$'), views.set_jabber_password, name='auth_set_jabber_password'),
)
