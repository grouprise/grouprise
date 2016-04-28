from . import models
import rules

@rules.predicate
def content_is_permitted(user, content):
    return content in models.Content.objects.permitted(user)

@rules.predicate
def is_content_author(user, content):
    return content.author == user.gestalt

rules.add_perm('content.view_content_list', rules.always_allow)
rules.add_perm('content.view_event_day', rules.always_allow)

rules.add_perm('content.view_content', content_is_permitted)
rules.add_perm('content.create_content', rules.is_authenticated)
rules.add_perm('content.change_content', rules.is_authenticated & is_content_author)

rules.add_perm('content.create_comment', rules.is_authenticated & content_is_permitted)
rules.add_perm('content.create_image', rules.is_authenticated & is_content_author)
