from rules import add_perm, always_allow, is_authenticated, predicate


@predicate
def is_content_author(user, content):
    return content.author == user.gestalt


add_perm('content.view_content', always_allow)
add_perm('content.change_content', is_authenticated & is_content_author)
