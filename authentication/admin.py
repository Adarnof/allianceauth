from __future__ import unicode_literals

from django.contrib import admin

from authentication.models import AuthServicesInfo
from eveonline.models import EveCharacter


@admin.register(AuthServicesInfo)
class AuthServicesInfoManager(admin.ModelAdmin):

    @staticmethod
    def main_character(obj):
        if obj.main_char_id:
            try:
                return EveCharacter.objects.get(character_id=obj.main_char_id)
            except EveCharacter.DoesNotExist:
                pass
        return None

    # TODO: This would be good to convert into a ServiceHook call
    """
    def sync_nicknames(self, request, queryset):
        count = 0
        for a in queryset:
            if a.discord_uid != "":
                update_discord_nickname(a.user.pk)
                count += 1
        self.message_user(request, "%s discord accounts queued for nickname sync." % count)

    sync_nicknames.short_description = "Sync nicknames for selected discord accounts"
    """

    search_fields = [
        'user__username',
        'ipboard_username',
        'xenforo_username',
        'forum_username',
        'jabber_username',
        'mumble_username',
        'teamspeak3_uid',
        'discord_uid',
        'ips4_username',
        'smf_username',
        'market_username',
        'main_char_id',
    ]
    list_display = ('user', 'main_character')
