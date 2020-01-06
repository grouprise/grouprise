from rules import add_perm, always_allow, is_authenticated, predicate
from grouprise.features.content.rules import can_view as content_can_view


@predicate
def is_attending(user, association):
    return association.container.attendance_statements.filter(attendee=user.gestalt).exists()


add_perm('events.view_day', always_allow)
add_perm('events.view_list', always_allow)
add_perm('events.can_change_attendance', is_authenticated & content_can_view)
add_perm('events.can_attend', is_authenticated & content_can_view & ~is_attending)
add_perm('events.can_abstain', is_authenticated & content_can_view & is_attending)
