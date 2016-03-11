from . import models
import rules

@rules.predicate
def content_is_permitted(user, content):
    return content in models.Content.objects.permitted(user)

@rules.predicate
def is_content_author(user, content):
    return content.author == user.gestalt

rules.add_perm('content.view_content', content_is_permitted)
rules.add_perm('content.change_content', rules.is_authenticated & is_content_author)
