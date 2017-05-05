"""
This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.
"""

import logging
import re

from django.apps import apps
from django.contrib.contenttypes import models as contenttypes
from django.db.models import signals
from stadt.settings import TAGS_TAGGABLE
from . import RE_TAG_REF
from .models import Tag, Tagged


logger = logging.getLogger(__name__)

_DEFAULT_CONF = {
    'tag_self': True,
    'constraint': lambda *args: True,
    'tag_related': []
}


class Index:
    index = None

    @classmethod
    def build(cls):
        cls.index = []
        for conf in TAGS_TAGGABLE:
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
        tag_map[Tag.slugify(tag_name)] = tag_name
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
            tags.extend(re.findall(RE_TAG_REF, getattr(instance, prop, '')))

        if len(tags) == 0:
            continue

        final_tags = build_tags(tags)

        tagged_models = []
        if conf['tag_self']:
            tagged_models.append(instance)
        for related in conf['tag_related']:
            tagged_models.append(related(instance))

        for tag in final_tags:
            for model in tagged_models:
                try:
                    tagged_type = contenttypes.ContentType.objects.get_for_model(model)
                except AttributeError:
                    logger.error("Failed to retrieve tagged type of model: %s", model)
                    continue
                Tagged.objects.get_or_create(
                    tag=tag, tagged_id=model.id,
                    tagged_type=tagged_type
                )


signals.post_save.connect(tag_entities)
