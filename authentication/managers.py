from __future__ import unicode_literals
from django.contrib.auth.models import User

from authentication.models import AuthServicesInfo

import logging

logger = logging.getLogger(__name__)


class AuthServicesInfoManager:
    def __init__(self):
        pass

    @staticmethod
    def update_main_char_id(char_id, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s main character to id %s" % (user, char_id))
            authserviceinfo = AuthServicesInfo.objects.get_or_create(user=user)[0]
            authserviceinfo.main_char_id = char_id
            authserviceinfo.save(update_fields=['main_char_id'])
            logger.info("Updated user %s main character to id %s" % (user, char_id))
        else:
            logger.error("Failed to update user %s main character id to %s: user does not exist." % (user, char_id))

    @staticmethod
    def update_is_blue(is_blue, user):
        if User.objects.filter(username=user.username).exists():
            logger.debug("Updating user %s blue status: %s" % (user, is_blue))
            authserviceinfo = AuthServicesInfo.objects.get_or_create(user=user)[0]
            authserviceinfo.is_blue = is_blue
            authserviceinfo.save(update_fields=['is_blue'])
            logger.info("Updated user %s blue status to %s in authservicesinfo model." % (user, is_blue))
