import os
from urlparse import urlparse

import xmpp
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.conf import settings
from openfire import exception
from openfire import UserService

from authentication.managers import AuthServicesInfoManager

import threading

import requests
import json

class OpenfireManager:
    def __init__(self):
        pass

    @staticmethod
    def send_broadcast_threaded(group_name, broadcast_message):
        broadcast_thread = XmppThread(1, "XMPP Broadcast Thread", 1, group_name, broadcast_message)
        broadcast_thread.start()

    @staticmethod
    def __add_address_to_username(username):
        address = urlparse(settings.OPENFIRE_ADDRESS).netloc.split(":")[0]
        completed_username = username + "@" + address
        return completed_username

    @staticmethod
    def __santatize_username(username):
        sanatized = username.replace(" ", "_")
        sanatized = sanatized.replace("'", "")
        return sanatized.lower()

    @staticmethod
    def __generate_random_pass():
        return os.urandom(8).encode('hex')

    @staticmethod
    def add_user(username):

        try:
            sanatized_username = OpenfireManager.__santatize_username(username)
            random_password = OpenfireManager.__generate_random_pass()
          
            openfire_path = settings.OPENFIRE_ADDRESS + "plugins/restapi/v1/users"
          
            user_details = {"username":sanatized_username, "password":random_password}                        
            custom_headers = {'authorization':settings.OPENFIRE_SECRET_KEY, 'content-type':'application/json'}          
            r = requests.post(openfire_path, headers=custom_headers, data=json.dumps(user_details))
          
            r.raise_for_status()
          
        except:
            # failed for some reason
            return "", ""

        return sanatized_username, random_password

    @staticmethod
    def delete_user(username):
        try:
            openfire_path = settings.OPENFIRE_ADDRESS + "plugins/restapi/v1/users/" + username
            custom_headers = {'authorization': settings.OPENFIRE_SECRET_KEY}
            r = requests.delete(openfire_path, headers=custom_headers)

            r.raise_for_status()

            return True
        except:
            return False

    @staticmethod
    def lock_user(username):
        custom_headers = {'authorization': settings.OPENFIRE_SECRET_KEY}
        openfire_path = settings.OPENFIRE_ADDRESS + "plugins/restapi/v1/lockouts/" + username
        r = requests.post(openfire_path, headers=custom_headers)

    @staticmethod
    def unlock_user(username):
        custom_headers = {'authorization': settings.OPENFIRE_SECRET_KEY}
        openfire_path = settings.OPENFIRE_ADDRESS + "plugins/restapi/v1/lockouts/" + username
        r = requests.delete(openfire_path, headers=custom_headers)

    @staticmethod
    def update_user_pass(username):
        try:
            random_password = OpenfireManager.__generate_random_pass()

            custom_headers = {'authorization': settings.OPENFIRE_SECRET_KEY, 'content-type':'application/json'}
            openfire_path = settings.OPENFIRE_ADDRESS + "plugins/restapi/v1/users/" + username
            user_details = {"username": sanatized_username, "password": random_password}

            r = requests.put(openfire_path, headers=custom_headers, data=json.dumps(user_details))

            r.raise_for_status()

            return random_password
        except:
            return ""

    @staticmethod
    def update_user_groups(username, password, groups):
        openfire_path = settings.OPENFIRE_ADDRESS + "plugins/restapi/v1/users/" + username + "/groups"
        #this endpoint doesn't allow put (boohoo) so we have to run a comparison on local vs remote groups
        custom_headers = {'authorization': settings.OPENFIRE_SECRET_KEY, 'accept': 'application/json'}
        r = requests.get(openfire_path, headers=custom_headers)
        remote_groups = []
        remote_groups.append(r.json()['groupname'])
        delete_groups = []
        add_groups = []
        for g in remote_groups:
            if not g in groups:
                delete_groups.append(g)
        for g in groups:
            if not g in remote_groups:
                add_groups.append(g)

        custom_headers = {'authorization': settings.OPENFIRE_SECRET_KEY, 'content-type': 'application/json'}
        if delete_groups:
            delete_dict = {'groupname': delete_groups}
            r = requests.delete(openfire_path, headers=custom_headers, data=json.dumps(delete_dict))
        if add_groups:       
            add_dict = {'groupname': add_groups}
            r = requests.post(openfire_path, headers=custom_headers, data=json.dumps(add_dict))

    @staticmethod
    def delete_user_groups(username, groups):

        openfire_path = settings.OPENFIRE_ADDRESS + "plugins/restapi/v1/users/" + username + "/groups"
        custom_headers = {'authorization': settings.OPENFIRE_SECRET_KEY, 'content-type': 'application/json'}
        group_dict = {'groupname': groups}
        r = requests.delete(openfire_path, headers=custom_headers, data=json.dumps(group_dict))

    @staticmethod
    def send_broadcast_message(group_name, broadcast_message):
        # create to address
        client = xmpp.Client(settings.JABBER_URL)
        client.connect(server=(settings.JABBER_SERVER, settings.JABBER_PORT))
        client.auth(settings.BROADCAST_USER, settings.BROADCAST_USER_PASSWORD, 'broadcast')

        to_address = group_name + '@' + settings.BROADCAST_SERVICE_NAME + '.' + settings.JABBER_URL
        message = xmpp.Message(to_address, broadcast_message)
        message.setAttr('type', 'chat')
        client.send(message)
        client.Process(1)

        client.disconnect()


class XmppThread (threading.Thread):
    def __init__(self, threadID, name, counter, group, message,):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.group = group
        self.message = message

    def run(self):
        print "Starting " + self.name
        OpenfireManager.send_broadcast_message(self.group, self.message)
        print "Exiting " + self.name
