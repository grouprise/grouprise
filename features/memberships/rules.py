import rules
import rules.permissions
from rules import add_perm, is_authenticated

from features.groups import rules as groups
from features.groups.rules import is_closed
from features.memberships.predicates import is_member_of
from . import predicates as memberships


rules.add_perm(
        'memberships.join_group',
        rules.is_authenticated
        & ~ memberships.is_member_of
        & ~ groups.is_closed)

add_perm(
        'memberships.try_to_join',
        (~is_authenticated & ~is_closed) | (is_authenticated & ~is_closed & ~is_member_of))

rules.add_perm(
        'memberships.create_membership',
        rules.is_authenticated
        & groups.is_closed
        & memberships.is_member_of)

rules.add_perm(
        'memberships.delete_membership',
        rules.is_authenticated
        & memberships.is_member)

rules.add_perm(
        'memberships.view_list',
        rules.is_authenticated
        & memberships.is_member_of)

rules.add_perm(
        'memberships.apply',
        groups.is_group
        & groups.is_closed
        & rules.is_authenticated
        & ~ memberships.is_member_of)

rules.add_perm(
        'memberships.accept_application',
        ~ memberships.applicant_is_member
        & rules.is_authenticated
        & memberships.is_member_of_application_group)
