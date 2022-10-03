import logging
from typing import Sequence

from asgiref.sync import async_to_sync, sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from huey.contrib.djhuey import db_task

from grouprise.core.matrix import MatrixError, MATRIX_ROOM_POWER_LEVEL_MODERATOR
from grouprise.core.settings import get_grouprise_baseurl, get_grouprise_site
from grouprise.core.tasks import TaskPriority
from grouprise.features.gestalten.models import Gestalt
from .matrix_bot import (
    ChatBot,
    GESTALT_SETTINGS_CATEGORY_MATRIX,
    GESTALT_SETTINGS_KEY_PRIVATE_NOTIFICATION_ROOM,
)
from .notifications import MatrixMessage


logger = logging.getLogger(__name__)

# Some tasks should be attempted again in case of temporary failures of the Matrix server.
# Only tasks that are relevant and that interact with the Matrix server should use this feature.
MATRIX_CHAT_RETRIES = 2
MATRIX_CHAT_RETRY_DELAY = 30


def get_gestalt_matrix_notification_room(
    gestalt: Gestalt, create_if_missing: bool = True
):
    """retrieve the currently configured private room shared by the bot and the user

    Depending on `create_if_missing`, either `None` is returned or a new matrix room is created,
    if no room was configured for the user, yet.
    """
    try:
        return gestalt.settings.get(
            name=GESTALT_SETTINGS_KEY_PRIVATE_NOTIFICATION_ROOM,
            category=GESTALT_SETTINGS_CATEGORY_MATRIX,
        ).value
    except ObjectDoesNotExist:
        if create_if_missing:
            return create_gestalt_matrix_notification_room(gestalt)
        else:
            return None


def set_gestalt_matrix_notification_room(gestalt, room_id):
    try:
        room_setting = gestalt.settings.get(
            name=GESTALT_SETTINGS_KEY_PRIVATE_NOTIFICATION_ROOM,
            category=GESTALT_SETTINGS_CATEGORY_MATRIX,
        )
    except ObjectDoesNotExist:
        gestalt.settings.create(
            name=GESTALT_SETTINGS_KEY_PRIVATE_NOTIFICATION_ROOM,
            category=GESTALT_SETTINGS_CATEGORY_MATRIX,
            value=room_id,
        )
    else:
        room_setting.value = room_id
        room_setting.save()


def delete_gestalt_matrix_notification_room(gestalt):
    gestalt.settings.filter(
        name=GESTALT_SETTINGS_KEY_PRIVATE_NOTIFICATION_ROOM,
        category=GESTALT_SETTINGS_CATEGORY_MATRIX,
    ).delete()


def create_gestalt_matrix_notification_room(gestalt: Gestalt) -> str:
    """invite the user into a new room and store the room ID

    Raises MatrixError in case of problems.
    """

    async def _create_private_room():
        async with ChatBot() as bot:
            room_id = await bot.create_private_room(room_title, room_description)
            # raise the default power level for new members to "moderator"
            await bot._change_room_state(
                room_id,
                {"users_default": MATRIX_ROOM_POWER_LEVEL_MODERATOR},
                "m.room.power_levels",
                room_label=room_label,
            )
            # invite the target user
            await bot.invite_into_room(room_id, gestalt, room_label)
            return room_id

    room_title = _("{site_name} - notifications").format(
        site_name=get_grouprise_site().name
    )
    room_description = _("Notifications for private messages from {site_url}").format(
        site_url=get_grouprise_baseurl()
    )
    # the label is used for log messages only
    gestalt_label = str(gestalt)
    room_label = f"notifications for {gestalt_label}"
    room_id = async_to_sync(_create_private_room())()
    set_gestalt_matrix_notification_room(gestalt, room_id)
    return room_id


@db_task(name="sync_group_rooms_delayed", priority=TaskPriority.SYNCHRONIZATION)
@async_to_sync
async def sync_group_rooms_delayed(group):
    async with ChatBot() as bot:
        try:
            async for room in bot.synchronize_rooms_of_group(group):
                pass
        except MatrixError as exc:
            group_label = await sync_to_async(str)(group)
            logger.warning(
                f"Failed to synchronize group ({group_label}) with matrix rooms: {exc}"
            )


@db_task(
    retries=MATRIX_CHAT_RETRIES,
    retry_delay=MATRIX_CHAT_RETRY_DELAY,
    priority=TaskPriority.NOTIFICATION,
    name="send_invitations_for_gestalt",
)
@async_to_sync
async def send_invitations_for_gestalt(gestalt):
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


@db_task(
    retries=MATRIX_CHAT_RETRIES,
    retry_delay=MATRIX_CHAT_RETRY_DELAY,
    priority=TaskPriority.SYNCHRONIZATION,
    name="invite_to_group_rooms",
)
@async_to_sync
async def invite_to_group_rooms(group):
    async with ChatBot() as bot:
        try:
            async for invited in bot.send_invitations_to_group_members(group):
                logger.info(f"Invitation sent: {invited}")
        except MatrixError as exc:
            group_label = await sync_to_async(str)(group)
            logger.warning(
                f"Failed to invite new group members ({group_label}) to matrix rooms: {exc}"
            )


def _get_room_url(room_object):
    return get_grouprise_baseurl() + room_object.group.get_absolute_url()


@db_task(
    retries=MATRIX_CHAT_RETRIES,
    retry_delay=MATRIX_CHAT_RETRY_DELAY,
    priority=TaskPriority.SYNCHRONIZATION,
    name="migrate_to_new_room",
)
@async_to_sync
async def migrate_to_new_room(room_object, old_room_id, room_alias, new_room_id):
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
            await bot.send_text(old_room_id, text, msgtype="m.message")
        except MatrixError as exc:
            logger.warning(f"Failed to send goodbye message to {old_room_id}: {exc}")


@db_task(
    retries=MATRIX_CHAT_RETRIES,
    retry_delay=MATRIX_CHAT_RETRY_DELAY,
    priority=TaskPriority.SYNCHRONIZATION,
    name="kick_gestalt_from_group_matrix_rooms",
)
@async_to_sync
async def kick_gestalt_from_group_matrix_rooms(group, gestalt):
    async with ChatBot() as bot:
        try:
            await bot.kick_gestalt_from_group_rooms(group, gestalt)
        except MatrixError as exc:
            group_label = await sync_to_async(str)(group)
            logger.warning(
                f"Failed to kick previous group members ({group_label}) from matrix rooms: {exc}"
            )


@db_task(
    retries=MATRIX_CHAT_RETRIES,
    retry_delay=MATRIX_CHAT_RETRY_DELAY,
    priority=TaskPriority.NOTIFICATION,
    name="send_matrix_messages",
)
@async_to_sync
async def send_matrix_messages(
    messages: Sequence[MatrixMessage], message_type: str
) -> None:
    async with ChatBot() as bot:
        for message in messages:
            try:
                await bot.send_text(message.room_id, message.text, msgtype="m.message")
            except MatrixError as exc:
                logger.warning(f"Failed to send {message_type}: {exc}")
