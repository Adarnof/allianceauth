from models import AuthGroup
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from eveonline.models import EveCharacter
from util.common_task import add_user_to_group
from util.common_task import remove_user_from_group

class AuthGroupManager:
    def __init__(self):
        pass
    
    @staticmethod
    def create_authgroup(groupname, owner, hidden=False, description=None, parent=None):
        created=False
        if not AuthGroup.objects.filter(group=group).exists():
            #generate group model to assign
            group, gcreated = Group.objects.get_or_create(name=groupname)
            #generate new AuthGroup with spec'd parameters
            auth_group, created = AuthGroup.objects.get_or_create(group=group, owner=owner, hidden=hidden, description=description, parent=parent)
        #I'd like to use this return value for error handling
        return created
    
    @staticmethod
    def add_admins_to_authgroup(character_names, groupname):
        users = []
        for char in character_names:
            #get user models to assign to admin
            evechar = EveCharacter.objects.get(character_name=char)
            users.append(evechar.user)
        #retrieve the authgroup model
        auth_group = AuthGroup.objects.get(group.name=groupname)
        #perform the assignment
        auth_group.admins.add(users)
        #remove new admins from members list
        auth_group.members.remove(users)
        #add group to new admins
        for u in users:
            add_user_to_group(u, groupname)
        auth_group.save()

    @staticmethod
    def remove_admin_from_authgroup(character_name, groupname)
        user = EveCharacter.objects.get(character_name=character_name).user
        auth_group = AuthGroup.objects.get(group.name=groupname)
        auth_group.admins.remove(user)
        auth_group.members.add(user)
        auth_group.save()

    @staticmethod
    def add_member_to_authgroup(user, groupname):
        #removes user from members list of AuthGroup and then removes group from User
        auth_group = AuthGroup.objects.get(group.name=groupname)
        #ensure we're not double-adding a user
        if (user in auth_group.admins) or (auth_group.owner = user) or (user in auth_group.members):
            pass
        else
            auth_group.members.add(user)
            add_user_to_group(user, groupname)
            auth_group.save()

    @staticmethod
    def remvove_member_from_authgroup(user, groupname):
        auth_group = AuthGroup.objects.get(group.name=groupname)
        if user in auth_group.admins:
            auth_group.admins.remove(user)
        elif user in auth_group.members:
            auth_group.members.remove(user)
            remove_user_from_group(user, groupname)
        auth_group.save()

    @staticmethod
    def delete_authgroup(groupname)
        #remove all user associations with group, then strip owner group, then delete model
        auth_group = AuthGroup.objects.get(group.name=groupname)
        for m in auth_group.members:
            remove_member_from_authgroup(m, groupname)
        for a in auth_group.admins:
            remove_member_from_authgroup(a, groupname)
        remove_user_from_group(auth_group.owner, groupname)
        auth_group.delete()

    @staticmethod
    def change_authgroup_owner(user, groupname)
        auth_group = AuthGroup.objects.get(group.name=groupname)
        oldowner = auth_group.owner
        auth_group.owner = user
        auth_group.save()
        #default behaviour is for owner to retain member status
        add_member_to_authgroup(user, groupname)
