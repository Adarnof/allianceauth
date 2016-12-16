from __future__ import unicode_literals

from django.apps import AppConfig


class MumbleServiceConfig(AppConfig):
    name = 'mumble'

    def ready(self):
        import services.signals
