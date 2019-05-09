from rules import add_perm, is_authenticated, predicate

from grouprise.features.content.rules import is_member_of_associated_group
from grouprise.features.conversations.rules import can_view


@predicate
def can_access(user, contribution):
    for association in contribution.container.associations.all():
        if can_view(user, association):
            return True
    return False


@predicate
def is_conversation(user, contribution):
    return contribution.container.is_conversation


@predicate
def is_creator(user, contribution):
    return contribution.author == user.gestalt


@predicate
def is_multi_user_contribution(user, contribution):
    associations = contribution.container.associations
    return associations.count() > 1 or associations.first().entity.is_group


add_perm('contributions.delete', ~is_conversation & is_authenticated & is_creator)

add_perm('contributions.reply_to_author', is_multi_user_contribution & can_access)

add_perm('contributions.view_internal', is_authenticated & is_member_of_associated_group)
