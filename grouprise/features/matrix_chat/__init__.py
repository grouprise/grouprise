import collections


GESTALT_SETTINGS_CATEGORY_MATRIX = "matrix_chat"
GESTALT_SETTINGS_KEY_PRIVATE_NOTIFICATION_ROOM = "private_notifications_room_id"

MatrixMessage = collections.namedtuple("MatrixMessage", ("room_id", "text"))
