from __future__ import unicode_literals

from django.apps import AppConfig


class OpenfireServiceConfig(AppConfig):
    name = 'openfire'

    def ready(self):
        import services.signals
