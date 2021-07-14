import asyncio
import logging

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext as _
from huey.contrib.djhuey import db_task

from grouprise.core.settings import get_grouprise_baseurl
from grouprise.core.templatetags.defaultfilters import full_url
import grouprise.features.content.models
import grouprise.features.contributions.models
import grouprise.features.groups.models
import grouprise.features.memberships.models
from .matrix_bot import MatrixBot, MatrixError
from .models import (
    MatrixChatGestaltSettings,
    MatrixChatGroupRoom,
    MatrixChatGroupRoomInvitations,
)


logger = logging.getLogger(__name__)


@receiver(post_save, sender=MatrixChatGestaltSettings)
def post_matrix_chat_gestalt_settings_save(
    sender, instance, created, update_fields=None, **kwargs
):
    if created or (update_fields and "matrix_id_override" in update_fields):
        gestalt = instance.gestalt
        # the matrix ID of the user has changed: remove all existing invitations
        MatrixChatGroupRoomInvitations.objects.filter(gestalt=gestalt).delete()
        _send_invitations_for_gestalt(gestalt)


@db_task()
def _send_invitations_for_gestalt(gestalt):
    async def _invite_gestalt(gestalt):
        async with MatrixBot() as bot:
            for membership in gestalt.memberships.all():
                group = membership.group
                try:
                    async for invited in bot.send_invitations_to_group_members(
                        group, gestalten=[gestalt]
                    ):
                        logger.info(f"Invitation sent: {invited}")
                except MatrixError as exc:
                    logger.warning(
                        f"Failed to invite {gestalt} to matrix rooms of group {group}: {exc}"
                    )

    asyncio.run(_invite_gestalt(gestalt))


@receiver(post_save, sender=grouprise.features.groups.models.Group)
def create_matrix_rooms_for_new_group(sender, instance, created, **kwargs):
    if created:
        _sync_rooms_delayed(instance)


@db_task()
def _sync_rooms_delayed(group):
    async def _sync_rooms_async(group):
        async with MatrixBot() as bot:
            try:
                await bot.synchronize_rooms_of_group(group)
            except MatrixError as exc:
                logger.warning(
                    f"Failed to synchronize group ({group}) with matrix rooms: {exc}"
                )

    asyncio.run(_sync_rooms_async(group))


@db_task()
def send_matrix_room_messages(messages):
    async def _send_room_messages_async(messages):
        async with MatrixBot() as bot:
            for group, message, is_public in messages:
                for room in MatrixChatGroupRoom.objects.filter(group=group):
                    # send private messages only to the internal room
                    if is_public or room.is_private:
                        try:
                            await bot.send_text(room.room_id, message)
                        except MatrixError as exc:
                            logger.warning(
                                f"Failed to send matrix notification for contribution: {exc}"
                            )

    asyncio.run(_send_room_messages_async(messages))


@receiver(post_save, sender=grouprise.features.content.models.Content)
def send_content_notification_to_matrix_rooms(sender, instance, created, **kwargs):
    # For unknown reasons the instance is not complete at this moment
    # ("instance.get_associated_groups()" is empty).  Thus we delay the execution slightly by
    # asking our worker process to process the instance when it is ready.
    _delayed_send_content_notification_to_matrix_rooms(instance, created)


@db_task()
def _delayed_send_content_notification_to_matrix_rooms(instance, created):
    # only sent group messages to matrix rooms
    if instance.get_associated_groups():
        version = instance.versions.last()
        author = version.author
        if instance.is_event:
            content_type = "Termin"
        elif instance.is_file:
            content_type = "Anhang"
        elif instance.is_gallery:
            content_type = "Galerie"
        elif instance.is_poll:
            content_type = "Umfrage"
        elif instance.is_conversation:
            content_type = "Gespräch"
        else:
            content_type = "Artikel"
        change_type = "neu" if created else "aktualisiert"
        messages = []
        for association in instance.associations.all():
            if association.entity.is_group:
                group = association.entity
                url = full_url(association.get_absolute_url())
                summary = f"{content_type} ({change_type}): [{instance.subject} ({author})]({url})"
                messages.append((group, summary, association.public))
        send_matrix_room_messages(messages)


@receiver(post_save, sender=grouprise.features.contributions.models.Contribution)
def send_contribution_notification_to_matrix_rooms(sender, instance, created, **kwargs):
    if not created:
        # send notifications only for new contributions
        pass
    elif instance.deleted:
        # ignore deleted contributions
        pass
    elif not instance.container.get_associated_groups():
        # only sent group messages to matrix rooms
        pass
    else:
        author = instance.author
        messages = []
        for association in instance.container.associations.all():
            if association.entity.is_group:
                group = association.entity
                url = full_url(association.get_absolute_url())
                summary = f"Diskussionsbeitrag: [{instance.container.subject} ({author})]({url})"
                messages.append((group, summary, instance.public))
        send_matrix_room_messages(messages)


@receiver(post_save, sender=grouprise.features.memberships.models.Membership)
def synchronize_matrix_room_memberships(sender, instance, created, **kwargs):
    if created:
        _invite_to_group_rooms(instance.group)


@db_task()
def _invite_to_group_rooms(group):
    async def _invite_to_group_rooms_delayed(group):
        async with MatrixBot() as bot:
            try:
                async for invited in bot.send_invitations_to_group_members(group):
                    logger.info(f"Invitation sent: {invited}")
            except MatrixError as exc:
                logger.warning(
                    f"Failed to invite new group members ({group}) to matrix rooms: {exc}"
                )

    asyncio.run(_invite_to_group_rooms_delayed(group))


@receiver(pre_save, sender=MatrixChatGroupRoom)
def move_away_from_matrix_room(sender, instance, *args, update_fields=None, **kwargs):
    if (instance.id is not None) and update_fields and ("room_id" in update_fields):
        previous_room_id = MatrixChatGroupRoom.objects.get(pk=instance.pk).room_id
        _migrate_to_new_room(
            instance,
            previous_room_id,
            instance.get_default_room_alias(),
            instance.room_id,
        )
        # the old invitations are no longer of any use
        instance.invitations.all().delete()


@db_task()
def _migrate_to_new_room(*args):
    async def _migrate_to_new_room_delayed(
        room_object, old_room_id, room_alias, new_room_id
    ):
        async with MatrixBot() as bot:
            await bot.remove_room_alias(old_room_id, room_alias)
            text = _(
                'The {room_visibility} chat room of ["{group_name}"]({group_url})'
                " moved to {new_room_id}."
            ).format(
                room_visibility=_("private") if room_object.is_private else _("public"),
                group_url=(
                    get_grouprise_baseurl() + room_object.group.get_absolute_url()
                ),
                group_name=room_object.group.name,
                new_room_id=new_room_id,
            )
            try:
                await bot.send_text(old_room_id, text)
            except MatrixError as exc:
                logger.warning(
                    f"Failed to send goodbye message to {old_room_id}: {exc}"
                )

    asyncio.run(_migrate_to_new_room_delayed(*args))


@receiver(post_delete, sender=grouprise.features.memberships.models.Membership)
def kick_room_members_after_leaving_group(sender, instance, **kwargs):
    _kick_gestalt_from_group_rooms(instance.group, instance.member)


@db_task()
def _kick_gestalt_from_group_rooms(group, gestalt):
    async def _kick_gestalt_from_group_rooms_delayed(group, gestalt):
        async with MatrixBot() as bot:
            try:
                await bot.kick_gestalt_from_group_rooms(group, gestalt)
            except MatrixError as exc:
                logger.warning(
                    f"Failed to kick previous group members ({group}) from matrix rooms: {exc}"
                )

    asyncio.run(_kick_gestalt_from_group_rooms_delayed(group, gestalt))
