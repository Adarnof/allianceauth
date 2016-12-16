from __future__ import unicode_literals

from django.apps import AppConfig


class Ips4ServiceConfig(AppConfig):
    name = 'ips4'

    def ready(self):
        import services.signals
