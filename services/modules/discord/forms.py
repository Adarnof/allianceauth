from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _


class DiscordForm(forms.Form):
    email = forms.CharField(label=_("Email Address"), required=True)
    password = forms.CharField(label=_("Password"), required=True, widget=forms.PasswordInput)
    update_avatar = forms.BooleanField(label=_("Update Avatar"), required=False, initial=True)
