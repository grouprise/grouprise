import re
from markdown import Extension, util, inlinepatterns
from content.templatetags.content import markdown_extensions
from utils.markdown import ExtendedLinkPattern
from .models import Group
from . import RE_GROUP_REF


def get_group(m, index_base=0):
    slug = m.group(1 + index_base)
    try:
        group = Group.objects.get(slug=slug)
    except Group.DoesNotExist:
        group = None
    return group, slug, '@%s' % slug


def set_group_attrs(el, group_id):
    el.set('data-component', 'grouplink')
    el.set('data-grouplink-ref', str(group_id))
    return el


def get_group_placeholder(name):
    el = util.etree.Element('span')
    el.text = '%s (unbekannte Gruppe)' % name
    return el


class GroupLinkExtension:
    PROTO = r'group://(\d+)@(.*)'
    GROUP_NONE = 'group://none'

    def process_url(self, url):
        match = re.match(RE_GROUP_REF, url)

        if match:
            group, slug, name = get_group(match)
            if group:
                return 'group://%d@%s' % (group.id, group.get_absolute_url())
            else:
                return self.GROUP_NONE

    def process_link(self, a):
        el_href = a.get('href')
        match = re.match(self.PROTO, el_href)
        if match:
            group_id = match.group(1)
            href = match.group(2)
            a.set('href', href)
            set_group_attrs(a, group_id)
        elif el_href == self.GROUP_NONE:
            return get_group_placeholder(a.text)
        return a


class GroupReferencePattern(inlinepatterns.ReferencePattern):
    def handleMatch(self, m):
        group, slug, name = get_group(m, 1)

        if group:
            return set_group_attrs(
                self.makeTag(group.get_absolute_url(), str(group), name),
                group.id
            )
        else:
            return get_group_placeholder(name)


class GroupReferenceExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['group_reference'] = GroupReferencePattern(RE_GROUP_REF, md)


ExtendedLinkPattern.register_extension(GroupLinkExtension())
markdown_extensions.append(GroupReferenceExtension())
