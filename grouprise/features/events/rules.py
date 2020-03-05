from rules import add_perm, always_allow, is_authenticated, predicate

from grouprise.features.content.rules import can_view as content_can_view
from grouprise.features.associations.predicates import is_member
from . import GROUPRISE_CAN_ATTEND_GROUP_MEMBERS


@predicate
def is_attending(user, association):
    return association.container.attendance_statements.filter(attendee=user.gestalt).exists()


@predicate
def attending_group_members_is_allowed_by_configuration():
    return GROUPRISE_CAN_ATTEND_GROUP_MEMBERS


add_perm('events.view_day', always_allow)
add_perm('events.view_list', always_allow)
add_perm('events.can_change_attendance', is_authenticated & content_can_view)
add_perm('events.can_attend', is_authenticated & content_can_view & ~is_attending)
add_perm('events.can_abstain', is_authenticated & content_can_view & is_attending)
add_perm('events.can_attend_group_members',
         is_authenticated
         & is_member
         & attending_group_members_is_allowed_by_configuration)
