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


@receiver(post_save, sender=MatrixChatGestaltSettings)
def post_matrix_chat_gestalt_settings_save(
    sender, instance, created, update_fields=None, raw=False, **kwargs
):
    if not raw and (
        created or (update_fields and "matrix_id_override" in update_fields)
    ):
        gestalt = instance.gestalt
        # the matrix ID of the user has changed: remove all existing invitations
        MatrixChatGroupRoomInvitations.objects.filter(gestalt=gestalt).delete()
        send_invitations_for_gestalt(gestalt)
        # forget the old room for private messages (the former Matrix account still occupies it)
        delete_gestalt_matrix_notification_room(gestalt)


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
