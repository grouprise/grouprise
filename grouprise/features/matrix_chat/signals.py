from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

import grouprise.features.memberships.models
from grouprise.features.groups.models import Group
from grouprise.features.notifications.signals import register_notification_backend
from .models import (
    MatrixChatGestaltSettings,
    MatrixChatGroupRoom,
    MatrixChatGroupRoomInvitations,
)
from .notifications import (
    MatrixNotifications,
)
from .utils import (
    delete_gestalt_matrix_notification_room,
    invite_to_group_rooms,
    kick_matrix_id_from_group_room,
    migrate_to_new_room,
    send_invitations_for_gestalt,
    sync_group_rooms_delayed,
)

register_notification_backend(MatrixNotifications)


@receiver(pre_save, sender=MatrixChatGestaltSettings)
def pre_matrix_chat_gestalt_settings_save(sender, instance, raw, **kwargs):
    """before storing a new matrix ID, we have to get rid of references to the old one"""
    gestalt = instance.gestalt
    if not raw and (
        MatrixChatGestaltSettings.get_matrix_id(gestalt) != instance.matrix_id_override
    ):
        MatrixChatGroupRoomInvitations.objects.filter(gestalt=gestalt).delete()
        # forget the old room for private messages (the former Matrix account still occupies it)
        delete_gestalt_matrix_notification_room(gestalt)


@receiver(post_save, sender=MatrixChatGestaltSettings)
def post_matrix_chat_gestalt_settings_save(sender, instance, raw=False, **kwargs):
    gestalt = instance.gestalt
    if not raw:
        # We need to determine the new Matrix ID manually.
        # The `get_matrix_id` method does not work at the moment, since the reference to the new
        # MatrixChatGestaltSettings is stored in the related Gestalt *after* `instance` is saved.
        if instance.matrix_id_override is not None:
            new_matrix_id = instance.matrix_id_override
        else:
            new_matrix_id = MatrixChatGestaltSettings.get_default_local_matrix_id(
                gestalt
            )
        send_invitations_for_gestalt(gestalt, new_matrix_id)


@receiver(post_save, sender=Group)
def create_matrix_rooms_for_new_group(sender, instance, created, raw=False, **kwargs):
    if created and not raw:
        sync_group_rooms_delayed(instance)


@receiver(post_save, sender=grouprise.features.memberships.models.Membership)
def synchronize_matrix_room_memberships(sender, instance, created, raw=False, **kwargs):
    if created and not raw:
        invite_to_group_rooms(instance.group)


@receiver(pre_save, sender=MatrixChatGroupRoom)
def move_away_from_matrix_room(
    sender, instance, *args, update_fields=None, raw=False, **kwargs
):
    if (
        not raw
        and (instance.id is not None)
        and update_fields
        and ("room_id" in update_fields)
    ):
        previous_room_id = MatrixChatGroupRoom.objects.get(pk=instance.pk).room_id
        migrate_to_new_room(
            instance,
            previous_room_id,
            instance.get_default_room_alias(),
            instance.room_id,
        )
        # the old invitations are no longer of any use
        instance.invitations.all().delete()


@receiver(post_delete, sender=grouprise.features.memberships.models.Membership)
def kick_room_members_after_leaving_group(sender, instance, **kwargs):
    group = instance.group
    member = instance.member
    member_matrix_id = MatrixChatGestaltSettings.get_matrix_id(member)
    for room in group.matrix_rooms.all():
        # delete invitations
        MatrixChatGroupRoomInvitations.objects.filter(
            room=room, gestalt=member
        ).delete()
        kick_matrix_id_from_group_room(
            str(group), room.room_id, str(room), member_matrix_id
        )
