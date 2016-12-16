from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect

from authentication.decorators import members_and_blues
from eveonline.managers import EveManager
from eveonline.models import EveCharacter
from services.forms import ServicePasswordForm

from .manager import OpenfireManager
from .tasks import OpenfireTasks
from .forms import JabberBroadcastForm
from .models import OpenfireUser

import datetime

import logging

logger = logging.getLogger(__name__)


@login_required
@members_and_blues()
def activate_jabber(request):
    logger.debug("activate_jabber called by user %s" % request.user)
    character = EveManager.get_main_character(request.user)
    logger.debug("Adding jabber user for user %s with main character %s" % (request.user, character))
    info = OpenfireManager.add_user(character.character_name)
    # If our username is blank means we already had a user
    if info[0] is not "":
        OpenfireUser.objects.update_or_create(user=request.user, defaults={'username': info[0]})
        logger.debug("Updated authserviceinfo for user %s with jabber credentials. Updating groups." % request.user)
        OpenfireTasks.update_groups.delay(request.user.pk)
        logger.info("Successfully activated jabber for user %s" % request.user)
        messages.success(request, 'Activated jabber account.')
        credentials = {
            'username': info[0],
            'password': info[1],
        }
        return render(request, 'registered/service_credentials.html',
                      context={'credentials': credentials, 'service': 'Jabber'})
    else:
        logger.error("UnSuccessful attempt to activate jabber for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your jabber account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def deactivate_jabber(request):
    logger.debug("deactivate_jabber called by user %s" % request.user)
    if OpenfireTasks.has_account(request.user) and OpenfireTasks.delete_user(request.user):
        logger.info("Successfully deactivated jabber for user %s" % request.user)
        messages.success(request, 'Deactivated jabber account.')
    else:
        logger.error("UnSuccessful attempt to deactivate jabber for user %s" % request.user)
        messages.error(request, 'An error occurred while processing your jabber account.')
    return redirect("auth_services")


@login_required
@members_and_blues()
def reset_jabber_password(request):
    logger.debug("reset_jabber_password called by user %s" % request.user)
    if OpenfireTasks.has_account(request.user):
        result = OpenfireManager.update_user_pass(request.user.openfire.username)
        # If our username is blank means we failed
        if result != "":
            logger.info("Successfully reset jabber password for user %s" % request.user)
            messages.success(request, 'Reset jabber password.')
            credentials = {
                'username': request.user.openfire.username,
                'password': result,
            }
            return render(request, 'registered/service_credentials.html',
                          context={'credentials': credentials, 'service': 'Jabber'})
    logger.error("Unsuccessful attempt to reset jabber for user %s" % request.user)
    messages.error(request, 'An error occurred while processing your jabber account.')
    return redirect("auth_services")


@login_required
@permission_required('auth.jabber_broadcast')
def jabber_broadcast_view(request):
    logger.debug("jabber_broadcast_view called by user %s" % request.user)
    allchoices = []
    if request.user.has_perm('auth.jabber_broadcast_all'):
        allchoices.append(('all', 'all'))
        for g in Group.objects.all():
            allchoices.append((str(g.name), str(g.name)))
    else:
        for g in request.user.groups.all():
            allchoices.append((str(g.name), str(g.name)))
    if request.method == 'POST':
        form = JabberBroadcastForm(request.POST)
        form.fields['group'].choices = allchoices
        logger.debug("Received POST request containing form, valid: %s" % form.is_valid())
        if form.is_valid():
            main_char = EveManager.get_main_character(request.user)
            logger.debug("Processing jabber broadcast for user %s with main character %s" % (request.user, main_char))
            if main_char is not None:
                message_to_send = form.cleaned_data[
                                      'message'] + "\n##### SENT BY: " + "[" + main_char.corporation_ticker + "]" + \
                                  main_char.character_name + " TO: " + \
                                  form.cleaned_data['group'] + " WHEN: " + datetime.datetime.utcnow().strftime(
                    "%Y-%m-%d %H:%M:%S") + " #####\n##### Replies are NOT monitored #####\n"
                group_to_send = form.cleaned_data['group']

                OpenfireManager.send_broadcast_threaded(group_to_send, message_to_send, )

            else:
                message_to_send = form.cleaned_data[
                    'message'] + "\n##### SENT BY: " + "No character but can send pings?" + " TO: " + \
                    form.cleaned_data['group'] + " WHEN: " + datetime.datetime.utcnow().strftime(
                    "%Y-%m-%d %H:%M:%S") + " #####\n##### Replies are NOT monitored #####\n"
                group_to_send = form.cleaned_data['group']

                OpenfireManager.send_broadcast_threaded(group_to_send, message_to_send, )

            messages.success(request, 'Sent jabber broadcast to %s' % group_to_send)
            logger.info("Sent jabber broadcast on behalf of user %s" % request.user)
    else:
        form = JabberBroadcastForm()
        form.fields['group'].choices = allchoices
        logger.debug("Generated broadcast form for user %s containing %s groups" % (
            request.user, len(form.fields['group'].choices)))

    context = {'form': form}
    return render(request, 'registered/jabberbroadcast.html', context=context)


@login_required
@members_and_blues()
def set_jabber_password(request):
    logger.debug("set_jabber_password called by user %s" % request.user)
    if request.method == 'POST':
        logger.debug("Received POST request with form.")
        form = ServicePasswordForm(request.POST)
        logger.debug("Form is valid: %s" % form.is_valid())
        if form.is_valid() and OpenfireTasks.has_account(request.user):
            password = form.cleaned_data['password']
            logger.debug("Form contains password of length %s" % len(password))
            result = OpenfireManager.update_user_pass(request.user.openfire.username, password=password)
            if result != "":
                logger.info("Successfully set jabber password for user %s" % request.user)
                messages.success(request, 'Set jabber password.')
            else:
                logger.error("Failed to install custom jabber password for user %s" % request.user)
                messages.error(request, 'An error occurred while processing your jabber account.')
            return redirect("auth_services")
    else:
        logger.debug("Request is not type POST - providing empty form.")
        form = ServicePasswordForm()

    logger.debug("Rendering form for user %s" % request.user)
    context = {'form': form, 'service': 'Jabber'}
    return render(request, 'registered/service_password.html', context=context)
