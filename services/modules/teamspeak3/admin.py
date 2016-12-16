from __future__ import unicode_literals
from django.contrib import admin
from .models import AuthTS


class AuthTSgroupAdmin(admin.ModelAdmin):
    fields = ['auth_group', 'ts_group']
    filter_horizontal = ('ts_group',)


admin.site.register(AuthTS, AuthTSgroupAdmin)

