import re

from django import urls
from markdown import inlinepatterns, Extension

from grouprise.core.markdown import ExtendedLinkPattern, markdown_extensions
from grouprise.features.tags import RE_TAG_REF
from grouprise.features.tags.utils import get_slug


class TagLinkExtension:
    def process_url(self, url):
        match = re.match(RE_TAG_REF, url)
        if match:
            tag_name = match.group(1)
            tag_slug = get_slug(tag_name)
            return urls.reverse("tag", args=[tag_slug])

    def process_link(self, a):
        return a


class TagReferencePattern(inlinepatterns.ReferencePattern):
    def handleMatch(self, m):
        name = m.group(2)
        slug = get_slug(name)
        return self.makeTag(urls.reverse("tag", args=[slug]), None, "#%s" % name)


class TagReferenceExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns["tag_reference"] = TagReferencePattern(RE_TAG_REF, md)


ExtendedLinkPattern.register_extension(TagLinkExtension())
markdown_extensions.append(TagReferenceExtension())
