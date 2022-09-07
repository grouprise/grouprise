from django.db import migrations
from taggit.models import Tag

from grouprise.features.content.models import Content
from grouprise.features.groups.models import Group


def merge_duplicates(*args):
    """find tags with the same name (but different case) and merge them into one"""
    processed = set()
    while True:
        for tag in Tag.objects.all():
            if tag.pk in processed:
                continue
            else:
                processed.add(tag.pk)
            # get all tag objects with the same name
            unifiable_tags = Tag.objects.filter(name__iexact=tag.name)
            # pick one of the tags as the target for the merge operation
            target = sorted(
                (item.taggit_taggeditem_items.count(), item) for item in unifiable_tags
            )[0][1]
            # the others are supposed to be merged into target
            others = unifiable_tags.exclude(pk=target.pk)
            if others.count() > 0:
                for other in others:
                    for model in (Content, Group):
                        for item in model.objects.filter(tags=other).prefetch_related(
                            "tags"
                        ):
                            item.tags.add(target)
                            item.tags.filter(pk=other.pk).delete()
                            item.save()
                # find the preferred slug - the shortest one does not contain a numeric suffix
                shortest_slug = sorted(
                    [target.slug] + [other.slug for other in others]
                )[0]
                # delete the other tags (avoiding slug collisions in the next step)
                for other in others:
                    if other.taggit_taggeditem_items.count() == 0:
                        other.delete()
                target.slug = shortest_slug
                target.save()
                # we deleted some tags: invalidate the old queryset and start again
                break
        else:
            # we went through the whole queryset, but all items were already processed
            break


def delete_unwanted_tags(*args):
    Tag.objects.filter(slug__startswith="contribution-").delete()


def delete_unused_tags(*args):
    for tag in Tag.objects.all():
        if tag.taggit_taggeditem_items.count() == 0:
            tag.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("tags", "0011_auto_20190624_1543"),
    ]

    operations = [
        migrations.RunPython(delete_unwanted_tags),
        migrations.RunPython(merge_duplicates),
        migrations.RunPython(delete_unused_tags),
    ]
