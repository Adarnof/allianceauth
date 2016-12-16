from __future__ import unicode_literals

from django.apps import AppConfig


class SmfServiceConfig(AppConfig):
    name = 'smf'

    def ready(self):
        import services.signals
