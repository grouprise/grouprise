import rules
import rules.permissions

from features.groups import rules as groups
from . import models
from .predicates import *


rules.add_perm(
        'memberships.join_group',
        rules.is_authenticated
        & ~is_member_of
        & ~groups.is_closed)

rules.add_perm(
        'memberships.create_membership',
        rules.is_authenticated
        & groups.is_closed
        & is_member_of)

rules.add_perm(
        'memberships.delete_membership',
        rules.is_authenticated
        & is_member)

rules.add_perm(
        'memberships.view_list',
        rules.is_authenticated
        & is_member_of)

rules.add_perm(
        'memberships.apply',
        groups.is_group
        & groups.is_closed
        & rules.is_authenticated
        & ~ is_member_of)

rules.add_perm(
        'memberships.accept_application',
        ~ applicant_is_member
        & rules.is_authenticated
        & is_member_of_application_group)
