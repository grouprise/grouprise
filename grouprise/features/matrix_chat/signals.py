import collections
import logging
from typing import Iterable, Sequence

from asgiref.sync import async_to_sync, sync_to_async
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext as _
from huey.contrib.djhuey import db_task

import grouprise.features.memberships.models
from grouprise.core.matrix import MatrixError
from grouprise.core.settings import get_grouprise_baseurl
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups.models import Group
from .matrix_bot import ChatBot
from .models import (
    MatrixChatGestaltSettings,
    MatrixChatGroupRoom,
    MatrixChatGroupRoomInvitations,
)
from .settings import MATRIX_SETTINGS
from .utils import (
    create_gestalt_matrix_notification_room,
    delete_gestalt_matrix_notification_room,
    get_gestalt_matrix_notification_room,
)

logger = logging.getLogger(__name__)

# Some tasks should be attempted again in case of temporary failures of the Matrix server.
# Only tasks that are relevant and that interact with the Matrix server should use this feature.
MATRIX_CHAT_RETRIES = 2
MATRIX_CHAT_RETRY_DELAY = 30


MatrixMessage = collections.namedtuple("MatrixMessage", ("room_id", "text"))


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
        _send_invitations_for_gestalt(gestalt)
        # forget the old room for private messages (the former Matrix account still occupies it)
        delete_gestalt_matrix_notification_room(gestalt)


@db_task(
    retries=MATRIX_CHAT_RETRIES,
    retry_delay=MATRIX_CHAT_RETRY_DELAY,
    name="_send_invitations_for_gestalt",
)
@async_to_sync
async def _send_invitations_for_gestalt(gestalt):
    def get_gestalt_memberships(gestalt):
        return list(gestalt.memberships.all())

    async with ChatBot() as bot:
        for membership in await sync_to_async(get_gestalt_memberships)(gestalt):
            group = membership.group
            try:
                async for invited in bot.send_invitations_to_group_members(
                    group, gestalten=[gestalt]
                ):
                    logger.info(f"Invitation sent: {invited}")
            except MatrixError as exc:
                gestalt_label = await sync_to_async(str)(gestalt)
                group_label = await sync_to_async(str)(group)
                logger.warning(
                    f"Failed to invite {gestalt_label} to matrix rooms of group {group_label}:"
                    f" {exc}"
                )


@receiver(post_save, sender=Group)
def create_matrix_rooms_for_new_group(sender, instance, created, raw=False, **kwargs):
    if created and not raw:
        _sync_rooms_delayed(instance)


@db_task(name="_sync_rooms_delayed")
@async_to_sync
async def _sync_rooms_delayed(group):
    async with ChatBot() as bot:
        try:
            async for room in bot.synchronize_rooms_of_group(group):
                pass
        except MatrixError as exc:
            group_label = await sync_to_async(str)(group)
            logger.warning(
                f"Failed to synchronize group ({group_label}) with matrix rooms: {exc}"
            )


def get_matrix_messages_for_group(
    group: Group, text: str, is_public: bool
) -> Iterable[MatrixMessage]:
    """return a generator of MatrixMessage instances for the given group

    Zero or more MatrixMessage instances can be returned - based the Matrix rooms of the group and
    the "is_public" flag.

    @param group: the target group for the message
    @param text: the message to be sent
    @param is_public: the public attribute of the source content or contribution
    """
    for room in group.matrix_rooms.all():
        # send private messages only to the internal room
        if is_public or room.is_private:
            yield MatrixMessage(room.room_id, text)


def get_matrix_messages_for_public(text: str) -> Iterable[MatrixMessage]:
    for room_id in MATRIX_SETTINGS.PUBLIC_LISTENER_ROOMS:
        yield MatrixMessage(room_id, text)


@db_task(
    retries=MATRIX_CHAT_RETRIES,
    retry_delay=MATRIX_CHAT_RETRY_DELAY,
    name="send_matrix_messages",
)
@async_to_sync
async def send_matrix_messages(
    messages: Sequence[MatrixMessage], message_type: str
) -> None:
    async with ChatBot() as bot:
        for message in messages:
            try:
                await bot.send_text(message.room_id, message.text)
            except MatrixError as exc:
                logger.warning(f"Failed to send {message_type}: {exc}")


@db_task(
    retries=MATRIX_CHAT_RETRIES,
    retry_delay=MATRIX_CHAT_RETRY_DELAY,
    name="send_private_message_to_gestalt",
)
@async_to_sync
async def send_private_message_to_gestalt(text: str, gestalt: Gestalt) -> None:
    """send the message to the target gestalt

    If this is the first message being sent, then we need to invite the gestalt into a new room
    first.
    This private room is memorized as a setting of the gestalt.
    """

    async with ChatBot() as bot:
        room_id = await sync_to_async(get_gestalt_matrix_notification_room)(gestalt)
        if room_id is None:
            await create_gestalt_matrix_notification_room(bot, gestalt)
        await bot.send_text(room_id, text)


@receiver(post_save, sender=grouprise.features.memberships.models.Membership)
def synchronize_matrix_room_memberships(sender, instance, created, raw=False, **kwargs):
    if created and not raw:
        _invite_to_group_rooms(instance.group)


@db_task(
    retries=MATRIX_CHAT_RETRIES,
    retry_delay=MATRIX_CHAT_RETRY_DELAY,
    name="_invite_to_group_rooms",
)
@async_to_sync
async def _invite_to_group_rooms(group):
    async with ChatBot() as bot:
        try:
            async for invited in bot.send_invitations_to_group_members(group):
                logger.info(f"Invitation sent: {invited}")
        except MatrixError as exc:
            group_label = await sync_to_async(str)(group)
            logger.warning(
                f"Failed to invite new group members ({group_label}) to matrix rooms: {exc}"
            )


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
        _migrate_to_new_room(
            instance,
            previous_room_id,
            instance.get_default_room_alias(),
            instance.room_id,
        )
        # the old invitations are no longer of any use
        instance.invitations.all().delete()


def _get_room_url(room_object):
    return get_grouprise_baseurl() + room_object.group.get_absolute_url()


@db_task(
    retries=MATRIX_CHAT_RETRIES,
    retry_delay=MATRIX_CHAT_RETRY_DELAY,
    name="_migrate_to_new_room",
)
@async_to_sync
async def _migrate_to_new_room(room_object, old_room_id, room_alias, new_room_id):
    async with ChatBot() as bot:
        await bot.remove_room_alias(old_room_id, room_alias)
        text = _(
            'The {room_visibility} chat room of ["{group_name}"]({group_url})'
            " moved to {new_room_id}."
        ).format(
            room_visibility=_("private") if room_object.is_private else _("public"),
            group_url=await sync_to_async(_get_room_url)(room_object),
            group_name=room_object.group.name,
            new_room_id=new_room_id,
        )
        try:
            await bot.send_text(old_room_id, text)
        except MatrixError as exc:
            logger.warning(f"Failed to send goodbye message to {old_room_id}: {exc}")


@receiver(post_delete, sender=grouprise.features.memberships.models.Membership)
def kick_room_members_after_leaving_group(sender, instance, **kwargs):
    _kick_gestalt_from_group_rooms(instance.group, instance.member)


@db_task(
    retries=MATRIX_CHAT_RETRIES,
    retry_delay=MATRIX_CHAT_RETRY_DELAY,
    name="_kick_gestalt_from_group_rooms",
)
@async_to_sync
async def _kick_gestalt_from_group_rooms(group, gestalt):
    async with ChatBot() as bot:
        try:
            await bot.kick_gestalt_from_group_rooms(group, gestalt)
        except MatrixError as exc:
            group_label = await sync_to_async(str)(group)
            logger.warning(
                f"Failed to kick previous group members ({group_label}) from matrix rooms: {exc}"
            )
