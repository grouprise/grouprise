from taggit.models import Tag


def get_slug(tag_name):
    try:
        return Tag.objects.get(name=tag_name).slug
    except Tag.DoesNotExist:
        return Tag().slugify(tag_name)
