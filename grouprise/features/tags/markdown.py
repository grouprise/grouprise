import re

from django import urls
from markdown import Extension, inlinepatterns, util
from taggit.models import Tag

from grouprise.core.markdown import ExtendedLinkPattern, markdown_extensions
from grouprise.features.tags import RE_TAG_REF
from grouprise.features.tags.utils import get_slug, get_tag_data


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
        tag: Tag = Tag.objects.get(name=name)
        tag_category, tag_name = get_tag_data(tag)
        return self.makeTag(
            urls.reverse("tag", args=[tag.slug]),
            tag_name,
            tag_category,
        )

    def makeTag(self, href, text, category: str = None):
        el = util.etree.Element("a")
        text_el = util.etree.SubElement(el, "span")
        text_el.text = text
        el.set("href", href)
        el.set("class", "tag")
        if category:
            el.set("data-tag-group-key", category.lower())
            el.set("data-tag-group-name", category)
        return el


class TagReferenceExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns["tag_reference"] = TagReferencePattern(RE_TAG_REF, md)


ExtendedLinkPattern.register_extension(TagLinkExtension())
markdown_extensions.append(TagReferenceExtension())
