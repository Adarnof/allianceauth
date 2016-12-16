from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.contrib.auth.models import User
from authentication.states import MEMBER_STATE, BLUE_STATE, NONE_STATE


@python_2_unicode_compatible
class AuthServicesInfo(models.Model):
    STATE_CHOICES = (
        (NONE_STATE, 'None'),
        (BLUE_STATE, 'Blue'),
        (MEMBER_STATE, 'Member'),
    )

    main_char_id = models.CharField(max_length=64, blank=True, default="")
    user = models.ForeignKey(User)
    state = models.CharField(blank=True, null=True, choices=STATE_CHOICES, default=NONE_STATE, max_length=10)

    def __str__(self):
        return self.user.username + ' - AuthInfo'
