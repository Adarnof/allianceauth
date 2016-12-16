from __future__ import unicode_literals

from django.apps import AppConfig


class DiscourseServiceConfig(AppConfig):
    name = 'discourse'

    def ready(self):
        import services.signals
