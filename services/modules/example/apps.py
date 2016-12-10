from __future__ import unicode_literals

from django.apps import AppConfig


class ExampleServiceConfig(AppConfig):
    name = 'example_service'

    def ready(self):
        import services.signals
