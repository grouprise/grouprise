# Generated by Django 2.1.9 on 2019-06-24 08:51

from django.db import migrations
from taggit.managers import _TaggableManager
from taggit.models import Tag, TaggedItem


def copy_tags(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Group = apps.get_model('groups', 'Group')
    Tagged = apps.get_model('tags', 'Tagged')
    for tagged in Tagged.objects.all():
        if tagged.tagged_type == ContentType.objects.get_for_model(Group):
            group = Group.objects.get(id=tagged.tagged_id)
            tag, _ = Tag.objects.get_or_create(name=tagged.tag.name, slug=tagged.tag.slug)
            mgr = _TaggableManager(
                    through=TaggedItem, model=Group, instance=group,
                    prefetch_cache_name='tags')
            mgr.add(tag)


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0022_auto_20190408_0027'),
        ('taggit', '0003_taggeditem_add_unique_index'),
    ]

    operations = [
        migrations.RunPython(copy_tags),
    ]
