from .settings import MATRIX_SETTINGS

import rules


@rules.predicate
def is_matrix_chat_enabled():
    return MATRIX_SETTINGS.ENABLED


@rules.predicate
def matrix_chat_room_has_members(room):
    return room and (room.members_count > 0)


# Evaluating this rule returns False if the "matrix_chat" application is not installed
# (see INSTALLED_APPS).  It returns True, if the application is installed and the corresponding
# setting is True.
rules.add_rule("is_matrix_chat_enabled", is_matrix_chat_enabled)
rules.add_rule("matrix_chat.room_is_populated", matrix_chat_room_has_members)
