from . import models
import rules

@rules.predicate
def is_permitted(user, content):
    if content:
        return models.Content.objects.permitted(user).filter(pk=content.pk).exists()
    return False

@rules.predicate
def is_author(user, content):
    return content.author == user.gestalt

@rules.predicate
def is_group_content(user, content):
    return content.groups.exists()

@rules.predicate
def is_group_member(user, content):
    for group in content.groups.all():
        if group.members.filter(pk=user.gestalt.pk).exists():
            return True
    return False

@rules.predicate
def is_public(user, content):
    return content.public

rules.add_perm('content.view_content_list', rules.always_allow)
rules.add_perm('content.view_event_day', rules.always_allow)
rules.add_perm('content.view_help', rules.always_allow)

rules.add_perm('content.view_content', is_permitted)
rules.add_perm('content.view_author', is_permitted & (~is_group_content | ~is_public | (rules.is_authenticated & (is_author | is_group_member))))
rules.add_perm('content.create_content', rules.is_authenticated)
rules.add_perm('content.change_content', rules.is_authenticated & is_author)

rules.add_perm('content.create_comment', rules.is_authenticated & is_permitted)
rules.add_perm('content.create_image', rules.is_authenticated & is_author)
rules.add_perm('content.view_image_list', is_permitted)
