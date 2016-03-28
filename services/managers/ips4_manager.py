import logging
from django.conf import settings
import requests
import os

logger = logging.getLogger(__name__)

class Ips4Manager:
    MEMBER_GROUP_ID = 3
    MEMBER_ENDPOINT = "/api/core/members"


    @staticmethod
    def __generate_random_pass():
        return os.urandom(8).encode('hex')

    @staticmethod
    def add_user(username, email):
        logger.debug("Adding new IPS4 user %s" % username)
        password = Ips4Manager.__generate_random_pass()
        data = {
            'name': username,
            'email': email,
            'password': password,
            'group': Ips4Manager.MEMBER_GROUP_ID,
        }
        try:
            r = requests.POST(settings.IPS4_URL + Ips4Manager.MEMBER_ENDPOINT, auth=(settings.IPS4_API_KEY, None), json=data)
            r.raise_for_status()
            id = r.json()['id']
            logger.info("Added IPS4 user %s" % username)
            return username, password, id
        except:
            logger.exception("Failed to add IPS4 user %s" % username)
            return None, None, 0

    @staticmethod
    def delete_user(id):
        logger.debug("Deleting IPS4 user id %s" % id)
        try:
            r = requests.DELETE(settings.IPS4_URL + Ips4Manager.MEMBER_ENDPOINT + "/%s" % id, auth=(settings.IPS4_API_KEY, None))
            r.raise_for_status()
            logger.info("Deleted IPS4 user %s" % id)
            return True
        except:
            logger.exception("Failed to delete IPS4 user id %s" % id)
            return False

    @staticmethod
    def update_user_password(username, email, id, password=None):
        logger.debug("Updating IPS4 user id %s password" % id)
        if not password:
            logger.debug("Generating random password")
            password = Ips4Manager.__generate_random_pass()
        data = {
            'name': username, 
            'email': email,
            'password': password,
        }
        try:
            r = requests.POST(settings.IPS4_URL + Ips4Manager.MEMBER_ENDPOINT + "/%s" % id, auth=(settings.IPS4_API_KEY, None), json=data)
            r.raise_for_status()
            logger.info("Reset IPS4 user %s password" % username)
            return password
        except:
            logger.exception("Failed to reset IPS4 user %s password" % username)
            return None
