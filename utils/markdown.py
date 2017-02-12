import re
import markdown
from markdown import blockprocessors, inlinepatterns, util
from features.groups import models as groups

RE_GROUP_REF = r'@([a-zA-Z_-]+)'
RE_GROUPLINK_REF = r'\[@([a-zA-Z_-]+)\](\(([^\)]+)\))?'


class CuddledListProcessor(blockprocessors.BlockProcessor):
    RE = re.compile(r'\n([*+-]|1\.)[ ]')

    def test(self, parent, block):
        return bool(self.RE.search(block))

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = self.RE.search(block)
        before = block[:m.start()]
        self.parser.parseBlocks(parent, [before])
        after = block[m.start():]
        self.parser.parseBlocks(parent, [after])


class CuddledListExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.parser.blockprocessors.add(
                'cuddledlist', CuddledListProcessor(md.parser), '<paragraph')


def get_group(m, index_base=0):
    slug = m.group(1 + index_base)
    try:
        group = groups.Group.objects.get(slug=slug)
    except groups.Group.DoesNotExist:
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


class GroupReferenceExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['group_reference'] = GroupReferencePattern(RE_GROUP_REF, md)


class GroupEnabledLinkPattern(inlinepatterns.LinkPattern):
    RE_GROUP_PROTO = r'group://(\d+)@(.*)'
    GROUP_NONE = 'group://none'

    def handleMatch(self, m):
        el = super().handleMatch(m)
        el_href = el.get('href')

        # in order to avoid any tampering with the original implementation
        # of LinkPattern we use sanitize_url to provide us with special
        # group url that we use to pass around group information
        match = re.match(self.RE_GROUP_PROTO, el_href)
        if match:
            group_id = match.group(1)
            href = match.group(2)
            el.set('href', href)
            set_group_attrs(el, group_id)
        elif el_href == self.GROUP_NONE:
            return get_group_placeholder(el.text)

        return el

    def sanitize_url(self, url):
        match = re.match(RE_GROUP_REF, url)

        if match:
            group, slug, name = get_group(match)
            if group:
                return 'group://%d@%s' % (group.id, group.get_absolute_url())
            else:
                return self.GROUP_NONE

        return super().sanitize_url(url)


class GroupEnabledLinkExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['link'] = GroupEnabledLinkPattern(inlinepatterns.LINK_RE, md)
