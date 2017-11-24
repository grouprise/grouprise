import re
from django.core import urlresolvers
from markdown import inlinepatterns, Extension
from core.markdown import ExtendedLinkPattern, markdown_extensions
from .models import Tag
from . import RE_TAG_REF


class TagLinkExtension:
    def process_url(self, url):
        match = re.match(RE_TAG_REF, url)
        if match:
            tag_name = match.group(1)
            tag_slug = Tag.slugify(tag_name)
            return urlresolvers.reverse('tag', args=[tag_slug])

    def process_link(self, a):
        return a


class TagReferencePattern(inlinepatterns.ReferencePattern):
    def handleMatch(self, m):
        name = m.group(2)
        slug = Tag.slugify(name)
        return self.makeTag(urlresolvers.reverse('tag', args=[slug]), None, '#%s' % name)


class TagReferenceExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['tag_reference'] = TagReferencePattern(RE_TAG_REF, md)


ExtendedLinkPattern.register_extension(TagLinkExtension())
markdown_extensions.append(TagReferenceExtension())
