from taggit.models import Tag


def get_slug(tag_name):
    try:
        return Tag.objects.get(name=tag_name).slug
    except Tag.DoesNotExist:
        return Tag().slugify(tag_name)


def get_tag_data(tag: Tag):
    tag_parts = tag.name.split(":", 1)
    if len(tag_parts) == 2:
        tag_group = tag_parts[0]
        tag_name = tag_parts[1]
    else:
        tag_group = None
        tag_name = tag.name
    return tag_group, tag_name
