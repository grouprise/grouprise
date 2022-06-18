from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

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
