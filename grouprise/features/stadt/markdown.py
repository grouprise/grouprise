import re

from django.db.models import Q
from markdown import Extension, util, inlinepatterns

from grouprise.core.markdown import ExtendedLinkPattern, markdown_extensions
from grouprise.core.templatetags.core import full_url
from grouprise.features.associations import models as associations
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups.models import Group
from . import RE_CONTENT_REF


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
    el.text = util.AtomicString('%s (unbekannte Gruppe/Gestalt)' % name)
    return el


class EntityLinkExtension:
    PROTO = r'(gestalt|group)://(\d+)@(.*)'
    ENTITY_NONE = 'entity://none'

    def process_url(self, url):
        match = re.match(RE_CONTENT_REF, url)

        if match:
            entity, slug, name = get_entity(match)
            if entity:
                entity_url = full_url(entity.get_absolute_url())
                if entity.is_group:
                    return 'group://%d@%s' % (entity.id, entity_url)
                else:
                    return 'gestalt://%d@%s' % (entity.id, entity_url)
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


ExtendedLinkPattern.register_extension(EntityLinkExtension())


class ContentReferencePattern(inlinepatterns.ReferencePattern):
    def handleMatch(self, m):
        entity_slug = m.group(2)
        content_slug = m.group(3)
        if content_slug:
            try:
                association = associations.Association.objects.get(
                        Q(group__slug=entity_slug) | Q(gestalt__user__username=entity_slug),
                        slug=content_slug)
                name = '@{}/{}'.format(entity_slug, content_slug)
                return self.makeTag(
                        full_url(association.get_absolute_url()), str(association), name)
            except associations.Association.DoesNotExist:
                pass
        entity, slug, name = get_entity(m, 1)
        if entity:
            return set_entity_attrs(
                self.makeTag(full_url(entity.get_absolute_url()), str(entity), name),
                entity.id,
                entity.is_group
            )
        else:
            return get_entity_placeholder(name)


class ContentReferenceExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['content_reference'] = ContentReferencePattern(RE_CONTENT_REF, md)


markdown_extensions.append(ContentReferenceExtension())
