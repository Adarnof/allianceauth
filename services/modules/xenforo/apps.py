from __future__ import unicode_literals

from django.apps import AppConfig


class XenforoServiceConfig(AppConfig):
    name = 'xenforo'

    def ready(self):
        import services.signals
