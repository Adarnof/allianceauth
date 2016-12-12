from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models


@python_2_unicode_compatible
class MumbleUser(models.Model):
    username = models.CharField(max_length=254, unique=True)
    pwhash = models.CharField(max_length=40)
    groups = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username
