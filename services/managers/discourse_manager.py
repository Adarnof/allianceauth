import logging
import requests
import os
import datetime
import json
from django.conf import settings
from django.utils import timezone
from services.models import GroupCache

logger = logging.getLogger(__name__)

# not exhaustive, only the ones we need
ENDPOINTS = {
    'groups': {
        'list': {
            'path': "/admin/groups.json",
            'method': requests.get,
            'args': {
                'required': [],
                'optional': [],
            },
        },
        'create': {
            'path': "/admin/groups",
            'method': requests.post,
            'args': {
                'required': ['name'],
                'optional': ['visible'],
            }
        },
        'add_user': {
            'path': "/admin/groups/%s/members.json",
            'method': requests.put,
            'args': {
                'required': ['usernames'],
                'optional': [],
            },
        },
        'remove_user': {
            'path': "/admin/groups/%s/members.json",
            'method': requests.delete,
            'args': {
                'required': ['username'],
                'optional': [],
            },
        },
        'delete': {
            'path': "/admin/groups/%s.json",
            'method': requests.delete,
            'args': {
                'required': [],
                'optional': [],
            },
        },
    },
    'users': {
        'create': {
            'path': "/users",
            'method': requests.post,
            'args': {
                'required': ['name', 'email', 'password', 'username'],
                'optional': ['active'],
            },
        },
        'update': {
            'path': "/users/%s",
            'method': requests.put,
            'args': {
                'required': ['params'],
                'optional': [],
            }
        },
        'get': {
            'path': "/users/%s.json",
            'method': requests.get,
            'args': {
                'required': [],
                'optional': [],
            },
        },
        'activate': {
            'path': "admin/users/%s/activate",
            'method': requests.put,
            'args': {
                'required': [],
                'optional': [],
            },
        },
        'deactivate': {
            'path': "/users/%s",
            'method': requests.put,
            'args': {
                'required': ['active'],
                'optional': [],
            },
        },
    },
}

class DiscourseManager:
    GROUP_CACHE_MAX_AGE = datetime.timedelta(minutes=30)
    REVOKED_EMAIL = 'revoked@' + settings.DOMAIN

    @staticmethod
    def __exc(endpoint, *args, **kwargs):
        params = {
            'api_key': settings.DISCOURSE_API_KEY,
            'api_username': settings.DISCOURSE_API_USERNAME,
        }
        if args:
            path = endpoint['path'] % args
        else:
            path = endpoint['path']
        data = {}
        for arg in endpoint['args']['required']:
            data[arg] = kwargs[arg]
        for arg in endpoint['args']['optional']:
            if arg in kwargs:
                data[arg] = kwargs[arg]
        for arg in kwargs:
            if not arg in endpoint['args']['required'] and not arg in endpoint['args']['optional']:
                logger.warn("Received unrecognized kwarg %s for endpoint %s" % (arg, endpoint))
        r = endpoint['method'](settings.DISCOURSE_URL + path, params=params, json=data)
        if 'errors' in r.json():
            logger.error("Discourse execution failed.\nEndpoint: %s\nErrors: %s" % (endpoint, r.json()['errors']))
        r.raise_for_status()
        if 'success' in r.json():
            if not r.json()['success']:
                raise ValueError()
        return r.json()

    @staticmethod
    def __generate_random_pass():
        return os.urandom(8).encode('hex')

    @staticmethod
    def __get_groups():
        endpoint = ENDPOINTS['groups']['list']
        data = DiscourseManager.__exc(endpoint)
        return [g for g in data if not g['automatic']]

    @staticmethod
    def __update_group_cache():
        GroupCache.objects.filter(service="discourse").delete()
        cache = GroupCache.objects.create(service="discourse")
        cache.groups = json.dumps(DiscourseManager.__get_groups())
        cache.save()
        return cache

    @staticmethod
    def __get_group_cache():
        if not GroupCache.objects.filter(service="discourse").exists():
            DiscourseManager.__update_group_cache()
        cache = GroupCache.objects.get(service="discourse")
        age = timezone.now() - cache.created
        if age > DiscourseManager.GROUP_CACHE_MAX_AGE:
            logger.debug("Group cache has expired. Triggering update.")
            cache = DiscourseManager.__update_group_cache()
        return json.loads(cache.groups)

    @staticmethod
    def __create_group(name):
        endpoint = ENDPOINTS['groups']['create']
        DiscourseManager.__exc(endpoint, name=name[:20], visible=True)
        DiscourseManager.__update_group_cache()

    @staticmethod
    def __group_name_to_id(name):
        cache = DiscourseManager.__get_group_cache()
        for g in cache:
            if g['name'] == name[0:20]:
                return g['id']
        logger.debug("Group %s not found on Discourse. Creating" % name)
        DiscourseManager.__create_group(name)
        return DiscourseManager.__group_name_to_id(name)

    @staticmethod
    def __group_id_to_name(id):
        cache = DiscourseManager.__get_group_cache()
        for g in cache:
            if g['id'] == id:
                return g['name']
        raise KeyError("Group ID %s not found on Discourse" % id)

    @staticmethod
    def __add_user_to_group(id, username):
        endpoint = ENDPOINTS['groups']['add_user']
        DiscourseManager.__exc(endpoint, id, usernames=[username])

    @staticmethod
    def __remove_user_from_group(id, username):
        endpoint = ENDPOINTS['groups']['remove_user']
        DiscourseManager.__exc(endpoint, id, username=username)

    @staticmethod
    def __generate_group_dict(names):
        dict = {}
        for name in names:
            dict[name] = DiscourseManager.__group_name_to_id(name)
        return dict

    @staticmethod
    def __get_user_groups(username):
        data = DiscourseManager.__get_user(username)
        return [g['id'] for g in data['user']['groups'] if not g['automatic']]

    @staticmethod
    def __user_name_to_id(name):
        data = DiscourseManager.__get_user(username)
        return data['user']['id']

    @staticmethod
    def __user_id_to_name(id):
        raise NotImplementedError

    @staticmethod
    def __get_user(username):
        endpoint = ENDPOINTS['users']['get']
        return DiscourseManager.__exc(endpoint, username)

    @staticmethod
    def __activate_user(username):
        endpoint = ENDPOINTS['users']['activate']
        id = DiscourseManager.__user_name_to_id(username)
        DiscourseManager.__exc(endpoint, id)

    @staticmethod
    def __update_user(username, **kwargs):
        endpoint = ENDPOINTS['users']['update']
        id = DiscourseManager.__user_name_to_id(username)
        DiscourseManager.__exc(endpoint, id, params=kwargs)

    @staticmethod
    def __create_user(username, email, password):
        endpoint = ENDPOINTS['users']['create']
        DiscourseManager.__exc(endpoint, name=username, username=username, email=email, password=password, active=True)

    @staticmethod
    def __check_if_user_exists(username):
        try:
            DiscourseManager.__get_user(username)
            return True
        except:
            return False
    @staticmethod
    def _sanatize_username(username):
        sanatized = username.replace(" ", "_")
        sanatized = sanatized.replace("'", "")
        return sanatized

    @staticmethod
    def add_user(username, email):
        logger.debug("Adding new discourse user %s" % username)
        password = DiscourseManager.__generate_random_pass()
        safe_username = DiscourseManager._sanatize_username(username)
        try:
            if DiscourseManager.__check_if_user_exists(username):
                logger.debug("Discourse user %s already exists. Reactivating" % username)
                DiscourseManager.__update_user(username, password=password, active=True)
            else:
                logger.debug("Creating new user account for %s" % username)
                DiscourseManager.__create_user(safe_username, email, password)
            logger.info("Added new discourse user %s" % username)
            return safe_username, password
        except:
            logger.exception("Failed to add new discourse user %s" % username)
            return "",""

    @staticmethod
    def update_user_password(username, password=None):
        logger.debug("Updating discourse user %s password" % username)
        if not password:
            password = DiscourseManager.__generate_random_pass()
        try:
            DiscourseManager.__update_user(username, password=password)
            logger.info("Updated discourse user %s password" % username)
            return password
        except:
            logger.exception("Failed to update discourse user %s password" % username)

    @staticmethod
    def delete_user(username):
        logger.debug("Deleting discourse user %s" % username)
        password = DiscourseManager.__generate_random_pass()
        try:
            DiscourseManager.__update_user(username, password=password, email=DiscourseManager.REVOKED_EMAIL, active=False)
            logger.info("Deleted discourse user %s" % username)
            return True
        except:
            logger.exception("Failed to delete discourse user %s" % username)
            return False

    @staticmethod
    def update_groups(username, raw_groups):
        groups = []
        for g in raw_groups:
            groups.append(g[:20])
        logger.debug("Updating discourse user %s groups to %s" % (username, groups))
        group_dict = DiscourseManager.__generate_group_dict(groups)
        inv_group_dict = {v:k for k,v in group_dict.items()}
        user_groups = DiscourseManager.__get_user_groups(username)
        add_groups = [group_dict[x] for x in group_dict if not group_dict[x] in user_groups]
        rem_groups = [x for x in user_groups if not inv_group_dict[x] in groups]
        if add_groups or rem_groups:
            logger.info("Updating discourse user %s groups: adding %s, removing %s" % (username, add_groups, rem_groups))
            for g in add_groups:
                DiscourseManager.__add_user_to_group(g, username)
            for g in rem_groups:
                DiscourseManager.__remove_user_from_group(g, username)
