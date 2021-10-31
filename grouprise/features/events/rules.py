from rules import add_perm, always_allow, is_authenticated, predicate

from grouprise.features.content.rules import can_view as content_can_view
from grouprise.features.memberships.predicates import is_member_of

from .settings import EVENT_SETTINGS


@predicate
def is_attending(user, association):
    return association.container.attendance_statements.filter(
        attendee=user.gestalt
    ).exists()


@predicate
def attending_group_members_is_allowed_by_configuration():
    return EVENT_SETTINGS.ALLOW_ATTENDANCE_MANAGEMENT_FOR_GROUP_MEMBERS


add_perm("events.view_day", always_allow)
add_perm("events.view_list", always_allow)
add_perm("events.can_change_attendance", is_authenticated & content_can_view)
add_perm("events.can_attend", is_authenticated & content_can_view & ~is_attending)
add_perm("events.can_abstain", is_authenticated & content_can_view & is_attending)
add_perm(
    "events.can_attend_group_members",
    is_authenticated
    & is_member_of
    & attending_group_members_is_allowed_by_configuration,
)
