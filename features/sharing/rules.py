from features.groups import rules as groups
from features.memberships import rules as memberships
import rules

rules.add_perm(
        'sharing.recommend_group',
        rules.always_allow)

rules.add_perm(
        'sharing.invite_member',
        memberships.is_member_of
        & ~groups.is_closed)
