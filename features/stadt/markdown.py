import re

from markdown import Extension, util, inlinepatterns

from core.markdown import markdown_extensions
from utils.markdown import ExtendedLinkPattern
from features.gestalten.models import Gestalt
from features.groups.models import Group
from . import RE_ENTITY_REF


def get_entity(m, index_base=0):
    slug = m.group(1 + index_base)
    try:
        entity = Group.objects.get(slug=slug)
    except Group.DoesNotExist:
        try:
            entity = Gestalt.objects.get(user__username=slug)
        except Gestalt.DoesNotExist:
            entity = None
    return entity, slug, '@%s' % slug


def set_entity_attrs(el, entity_id, is_group):
    if is_group:
        el.set('data-component', 'grouplink')
        el.set('data-grouplink-ref', str(entity_id))
    else:
        el.set('data-component', 'gestaltlink')
        el.set('data-gestaltlink-ref', str(entity_id))
    return el


def get_entity_placeholder(name):
    el = util.etree.Element('span')
    el.text = '%s (unbekannte Gruppe/Gestalt)' % name
    return el


class EntityLinkExtension:
    PROTO = r'(gestalt|group)://(\d+)@(.*)'
    ENTITY_NONE = 'entity://none'

    def process_url(self, url):
        match = re.match(RE_ENTITY_REF, url)

        if match:
            entity, slug, name = get_entity(match)
            if entity and entity.is_group:
                return 'group://%d@%s' % (entity.id, entity.get_absolute_url())
            elif entity:
                return 'gestalt://%d@%s' % (entity.id, entity.get_absolute_url())
            else:
                return self.ENTITY_NONE

    def process_link(self, a):
        el_href = a.get('href')
        match = re.match(self.PROTO, el_href)
        if match:
            entity_type = match.group(1)
            entity_id = match.group(2)
            href = match.group(3)
            a.set('href', href)
            set_entity_attrs(a, entity_id, entity_type == 'group')
        elif el_href == self.ENTITY_NONE:
            return get_entity_placeholder(a.text)
        return a


class EntityReferencePattern(inlinepatterns.ReferencePattern):
    def handleMatch(self, m):
        entity, slug, name = get_entity(m, 1)

        if entity:
            return set_entity_attrs(
                self.makeTag(entity.get_absolute_url(), str(entity), name),
                entity.id,
                entity.is_group
            )
        else:
            return get_entity_placeholder(name)


class EntityReferenceExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['entity_reference'] = EntityReferencePattern(RE_ENTITY_REF, md)


ExtendedLinkPattern.register_extension(EntityLinkExtension())
markdown_extensions.append(EntityReferenceExtension())
