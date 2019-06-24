import logging
import re

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes import models as contenttypes
from django.db.models import signals
from taggit.models import Tag

from grouprise.features.tags import RE_TAG_REF
from grouprise.features.tags.utils import get_slug


logger = logging.getLogger(__name__)

_DEFAULT_CONF = {
    'tag_self': False,
    'constraint': lambda *args: True,
    'tag_related': []
}


class Index:
    index = None

    @classmethod
    def build(cls):
        cls.index = []
        for conf in settings.GROUPRISE_TAGS_TAGGABLE:
            mconf = {}
            mconf.update(_DEFAULT_CONF)
            mconf.update(conf)
            entity = apps.get_model(mconf['entity'])
            mconf['entity'] = entity
            cls.index.append(mconf)

    @classmethod
    def is_initialized(cls):
        return cls.index is not None


def build_tags(tag_names):
    tag_map = {}
    tags = []
    for tag_name in tag_names:
        tag_map[get_slug(tag_name)] = tag_name
    for slug, name in tag_map.items():
        tag = Tag.objects.get_or_create(slug=slug, defaults={'name': name})[0]
        tags.append(tag)
    return tags


def tag_entities(sender, instance, *args, **kwargs):
    for conf in Index.index:
        if not isinstance(instance, conf['entity']):
            continue

        if not conf['constraint'](instance):
            continue

        tags = []
        for prop in conf['props']:
            attr = instance
            for e in prop.split('__'):
                attr = getattr(attr, e)
            tags.extend(re.findall(RE_TAG_REF, attr))

        if len(tags) == 0:
            continue

        final_tags = build_tags(tags)

        tagged_models = []
        print(conf)
        if conf['tag_self']:
            print('SELF')
            tagged_models.append(instance)
        for related in conf['tag_related']:
            print('RELATED')
            tagged_models.append(related(instance))
        print(tagged_models)

        for model in tagged_models:
            model.tags.add(*final_tags)


signals.post_save.connect(tag_entities)
