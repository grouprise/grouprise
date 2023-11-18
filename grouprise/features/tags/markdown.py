import re

import xml.etree.ElementTree as etree
from django import urls
from markdown import Extension, inlinepatterns
from taggit.models import Tag

from grouprise.core.markdown import ExtendedLinkPattern, markdown_extensions
from grouprise.features.tags import RE_TAG_REF
from grouprise.features.tags.utils import get_slug, get_tag_render_data


class TagLinkExtension:
    """allow tag links in URLs, e.g. `see [tag #foo](#foo)`

    This implementation differs from `EntityLinkExtension`: here we parse the text-based reference
    and directly emit a real URL. This leaves `process_link` as an empty stub.
    """

    def process_link(self, a):
        """substitute tag links in URLs"""
        url_match = re.match(RE_TAG_REF, a.get("href"))
        if url_match:
            tag_name = url_match.group(1)
            tag_slug = get_slug(tag_name)
            a.set("href", urls.reverse("tag", args=[tag_slug]))
        return a


class TagReferencePattern(inlinepatterns.ReferenceInlineProcessor):
    """replace tag-like tokens with a link to the tag overview

    Examples:
      - "Foo #Bar Baz"
      - "#Bar_Bus"
      - "#Bar:Bus"
    """

    def handleMatch(self, m, data):
        name = m.group(1)
        try:
            tag = Tag.objects.get(name__iexact=name)
        except Tag.DoesNotExist:
            tag = Tag.objects.create(name=name)
        except Tag.MultipleObjectsReturned:
            # TODO: remove this exception branch, when #770 is fixed
            tag = Tag.objects.filter(name__iexact=name).first()
        tag_group, tag_name = get_tag_render_data(name)
        result_tag = self.makeTag(
            urls.reverse("tag", args=[tag.slug]),
            tag_name,
            tag_group,
        )
        return (result_tag, *m.span())

    def makeTag(self, href, label, group_label: str = None):
        link_el = etree.Element("a")
        link_el.set("href", href)
        link_el.set("class", "tag")
        hash_el = etree.Element("span")
        hash_el.set("class", "tag-hash")
        hash_el.text = "#"
        if group_label:
            link_el.set("data-tag-group-key", group_label.lower())
            group_el = etree.Element("span")
            group_el.set("class", "tag-group")
            group_el.append(hash_el)
            # The element tail will be output AFTER the closing tag of the
            # element it’s assigned to. One might intuitively think it
            # should be assigned to the group_el, but that is not the case.
            hash_el.tail = group_label + ":"
            link_el.append(group_el)
        else:
            link_el.append(hash_el)
        label_el = etree.Element("span")
        label_el.set("class", "tag-name")
        label_el.text = label
        link_el.append(label_el)
        return link_el


class TagReferenceExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            TagReferencePattern(RE_TAG_REF.pattern, md), "tag_reference", 100
        )


ExtendedLinkPattern.register_extension(TagLinkExtension())
markdown_extensions.append(TagReferenceExtension())
