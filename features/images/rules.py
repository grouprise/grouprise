from content import rules as content
from features.associations import rules as associations
import rules


rules.add_perm(
        'content.create_image',
        rules.is_authenticated
        & (content.is_author
           | associations.is_member_of_any_content_group))

rules.add_perm(
        'content.update_image',
        rules.is_authenticated
        & content.is_author)

rules.add_perm(
        'content.view_image',
        content.is_permitted)

rules.add_perm(
        'content.view_image_list',
        content.is_permitted)
