from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _

from grouprise.core.settings import get_grouprise_baseurl, get_grouprise_site
from grouprise.features.gestalten.models import GestaltSetting


GESTALT_SETTINGS_KEY_PRIVATE_NOTIFICATION_ROOM = "private_notifications_room_id"
GESTALT_SETTINGS_CATEGORY_MATRIX = "matrix_chat"


def get_gestalt_matrix_notification_room(gestalt):
    try:
        return gestalt.settings.get(
            name=GESTALT_SETTINGS_KEY_PRIVATE_NOTIFICATION_ROOM,
            category=GESTALT_SETTINGS_CATEGORY_MATRIX,
        ).value
    except ObjectDoesNotExist:
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


def get_matrix_notification_room_queryset():
    return GestaltSetting.objects.filter(
        name=GESTALT_SETTINGS_KEY_PRIVATE_NOTIFICATION_ROOM,
        category=GESTALT_SETTINGS_CATEGORY_MATRIX,
    )


async def create_gestalt_matrix_notification_room(bot, gestalt) -> str:
    """invite the user into a new room and store the room ID

    Raises MatrixError in case of problems.
    """
    room_title = _("{site_name} - notifications").format(
        site_name=(await sync_to_async(get_grouprise_site)()).name
    )
    room_description = _("Notifications for private messages from {site_url}").format(
        site_url=await sync_to_async(get_grouprise_baseurl)()
    )
    # the label is used for log messages only
    gestalt_label = await sync_to_async(str)(gestalt)
    room_label = f"notifications for {gestalt_label}"
    # create the room
    room_id = await bot.create_private_room(room_title, room_description)
    # raise the default power level for new members to "moderator"
    await bot._change_room_state(
        room_id,
        {"users_default": 50},
        "m.room.power_levels",
        room_label=room_label,
    )
    # invite the target user
    await bot.invite_into_room(room_id, gestalt, room_label)
    await sync_to_async(set_gestalt_matrix_notification_room)(gestalt, room_id)
    return room_id
