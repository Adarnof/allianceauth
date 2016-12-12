from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from django.db import models


@python_2_unicode_compatible
class Ips4User(models.Model):
    user = models.OneToOneField(User,
                                primary_key=True,
                                on_delete=models.CASCADE,
                                related_name='ips4')
    username = models.CharField(max_length=254, blank=True, default="")
    id = models.CharField(max_length=254, blank=True, default="")

    def __str__(self):
        return self.username
