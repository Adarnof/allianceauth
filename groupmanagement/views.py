from django.template import RequestContext
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group

from models import GroupDescription
from models import GroupRequest
from models import HiddenGroup
from authentication.managers import AuthServicesInfoManager
from eveonline.managers import EveManager
from managers import AuthGroupManager
from forms import AuthGroupAddForm
from models import AuthGroup


@login_required
@permission_required('auth.group_management')
def group_management(request):
    acceptrequests = []
    leaverequests = []

    for grouprequest in GroupRequest.objects.all():
        if grouprequest.leave_request:
            leaverequests.append(grouprequest)
        else:
            acceptrequests.append(grouprequest)

    render_items = {'acceptrequests': acceptrequests, 'leaverequests': leaverequests}

    return render_to_response('registered/groupmanagement.html',
                              render_items, context_instance=RequestContext(request))


@login_required
@permission_required('auth.group_management')
def group_accept_request(request, group_request_id):
    try:
        group_request = GroupRequest.objects.get(id=group_request_id)
        group, created = Group.objects.get_or_create(name=group_request.group.name)
        group_request.user.groups.add(group)
        group_request.user.save()
        group_request.delete()
    except:
        pass

    return HttpResponseRedirect("/group/management/")


@login_required
@permission_required('auth.group_management')
def group_reject_request(request, group_request_id):
    try:
        group_request = GroupRequest.objects.get(id=group_request_id)

        if group_request:
            group_request.delete()
    except:
        pass

    return HttpResponseRedirect("/group/management/")


@login_required
@permission_required('auth.group_management')
def group_leave_accept_request(request, group_request_id):
    try:
        group_request = GroupRequest.objects.get(id=group_request_id)
        group, created = Group.objects.get_or_create(name=group_request.group.name)
        group_request.user.groups.remove(group)
        group_request.user.save()
        group_request.delete()
    except:
        pass

    return HttpResponseRedirect("/group/management/")


@login_required
@permission_required('auth.group_management')
def group_leave_reject_request(request, group_request_id):
    try:
        group_request = GroupRequest.objects.get(id=group_request_id)

        if group_request:
            group_request.delete()
    except:
        pass

    return HttpResponseRedirect("/group/management/")


@login_required
def groups_view(request):
    paired_list = []

    for group in Group.objects.all():
        # Check if group is a corp
        if "Corp_" in group.name:
            pass
        elif settings.DEFAULT_AUTH_GROUP in group.name:
            pass
        elif settings.DEFAULT_BLUE_GROUP in group.name:
            pass
        elif HiddenGroup.objects.filter(group=group).exists():
            pass
        else:
            # Get the descriptionn
            groupDesc = GroupDescription.objects.filter(group=group)
            groupRequest = GroupRequest.objects.filter(user=request.user).filter(group=group)

            if groupDesc:
                if groupRequest:
                    paired_list.append((group, groupDesc[0], groupRequest[0]))
                else:
                    paired_list.append((group, groupDesc[0], ""))
            else:
                if groupRequest:
                    paired_list.append((group, "", groupRequest[0]))
                else:
                    paired_list.append((group, "", ""))

    render_items = {'pairs': paired_list}
    return render_to_response('registered/groups.html',
                              render_items, context_instance=RequestContext(request))


@login_required
def group_request_add(request, group_id):
    auth_info = AuthServicesInfoManager.get_auth_service_info(request.user)
    grouprequest = GroupRequest()
    grouprequest.status = 'pending'
    grouprequest.group = Group.objects.get(id=group_id)
    grouprequest.user = request.user
    grouprequest.main_char = EveManager.get_character_by_id(auth_info.main_char_id)
    grouprequest.leave_request = False
    grouprequest.save()

    return HttpResponseRedirect("/groups")


@login_required
def group_request_leave(request, group_id):
    auth_info = AuthServicesInfoManager.get_auth_service_info(request.user)
    grouprequest = GroupRequest()
    grouprequest.status = 'pending'
    grouprequest.group = Group.objects.get(id=group_id)
    grouprequest.user = request.user
    grouprequest.main_char = EveManager.get_character_by_id(auth_info.main_char_id)
    grouprequest.leave_request = True
    grouprequest.save()

    return HttpResponseRedirect("/groups")

@login_required
def authgroup_add(request):
    success = False
    if request.method == 'POST':
        form = AuthGroupAddForm(request.POST, user=request.user)
        if form.is_valid():
            group_name = form.cleaned_data['group_name']
            owner = request.user
            group_description = form.cleaned_data['group_description']
            parent = form.cleaned_data['parent']
            hidden = form.cleaned_data['hidden']
            success = AuthGroupManager.create_authgroup(groupname=group_name, owner=owner, hidden=hidden, description=group_description, parent=parent)
    else:
        form = AuthGroupAddForm(user=request.user)

    context = {'form': form, 'success': success}

    return render_to_response('registered/groupadd.html', context, context_instance=RequestContext(request))

@login_required
def authgroup_list(request):
    user = request.user
    owner_groups = []
    admin_groups = []
    member_groups = []
    
    for a in AuthGroup.objects.all():
        if a.group.name == settings.DEFAULT_AUTH_GROUP:
            pass
        elif a.group.name == settings.DEFAULT_BLUE_GROUP:
            pass
        elif a.owner == user:
            owner_groups.append(a)
        elif user in a.admins.all():
            admin_groups.append(a)
        elif user in a.members.all():
            member_groups.append(a)

    render_items = {'owned': owner_groups, 'admin': admin_groups, 'member': member_groups}
    return render_to_response('registered/grouplist.html', render_items, context_instance=RequestContext(request))

@login_required
def authgroup_edit(request):
    return render_to_response('public/index.html', None, context_instance=RequestContext(request))

@login_required
def authgroup_delete(request, authgroup_name):
    render_items = {'group_name': authgroup_name}
    return render_to_response('registered/groupdelete.html', render_items, context_instance=RequestContext(request))
