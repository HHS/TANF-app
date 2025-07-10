"""Signals for the users app."""
from django.db.models.signals import m2m_changed, pre_save, post_save
from django.dispatch import receiver
from tdpservice.users.models import User
from django.contrib.auth.models import Group
from tdpservice.email.helpers.admin_notifications import email_system_owner_system_admin_role_change

import logging
logger = logging.getLogger()

@receiver(m2m_changed, sender=User.groups.through)
def user_group_changed(sender, instance, action, pk_set, **kwargs):
    """Send an email to the System Owner when a user is assigned or removed from the OFA System Admin role."""
    ACTIONS = {
            'PRE_REMOVE': 'pre_remove',
            'PRE_ADD': 'pre_add',
            'PRE_CLEAR': 'pre_clear'
        }
    if pk_set:
        ADMIN_GROUP_PK = Group.objects.get(name="OFA System Admin").pk
        group_change_list = [pk for pk in pk_set]
        if ADMIN_GROUP_PK in group_change_list and action == ACTIONS['PRE_ADD']:
            # EMAIL ADMIN GROUP ADDED to OFA ADMIN
            email_system_owner_system_admin_role_change(instance, "added")
        elif ADMIN_GROUP_PK in group_change_list and action == ACTIONS['PRE_REMOVE']:
            # EMAIL ADMIN GROUP REMOVED from OFA ADMIN
            email_system_owner_system_admin_role_change(instance, "removed")
    elif pk_set is None and action == ACTIONS['PRE_CLEAR']:
        # EMAIL ADMIN GROUP REMOVED from OFA ADMIN
        user = User.objects.get(pk=instance.pk)
        groups = [group.name for group in user.groups.all()]
        if "OFA System Admin" in groups:
            email_system_owner_system_admin_role_change(instance, "removed")

@receiver(pre_save, sender=User)
def user_is_staff_superuser_changed(sender, instance, **kwargs):
    """Send an email to the System Owner when a user is assigned or removed from the System Admin role."""
    # first get instance from db for existing state
    try:
        current_user_state = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return

    # check if is_staff is assigned
    if instance.is_staff and not current_user_state.is_staff:
        email_system_owner_system_admin_role_change(instance, "is_staff_assigned")
    # check if is_staff is removed
    elif not instance.is_staff and current_user_state.is_staff:
        email_system_owner_system_admin_role_change(instance, "is_staff_removed")
    # check if is_superuser is assigned
    if instance.is_superuser and not current_user_state.is_superuser:
        email_system_owner_system_admin_role_change(instance, "is_superuser_assigned")
    # check if is_superuser is removed
    elif not instance.is_superuser and current_user_state.is_superuser:
        email_system_owner_system_admin_role_change(instance, "is_superuser_removed")


@receiver(post_save, sender=User)
def user_is_staff_superuser_created(sender, instance, created, **kwargs):
    """Send an email to the System Owner when a user is assigned or removed from the System Admin role."""
    if created:
        if instance.is_staff:
            email_system_owner_system_admin_role_change(instance, "is_staff_assigned")
        if instance.is_superuser:
            email_system_owner_system_admin_role_change(instance, "is_superuser_assigned")
