import re

from django import urls
from markdown import Extension, inlinepatterns, util
from taggit.models import Tag

from grouprise.core.markdown import ExtendedLinkPattern, markdown_extensions
from grouprise.features.tags import RE_TAG_REF
from grouprise.features.tags.utils import get_slug, get_tag_render_data


class TagLinkExtension:
    def process_url(self, url):
        url_match = re.match(RE_TAG_REF, url)
        if url_match:
            tag_name = url_match.group(1)
            tag_slug = get_slug(tag_name)
            return urls.reverse("tag", args=[tag_slug])

    def process_link(self, a):
        return a


class TagReferencePattern(inlinepatterns.ReferencePattern):
    def handleMatch(self, m):
        name = m.group(2)
        try:
            tag = Tag.objects.get(name__iexact=name)
        except Tag.DoesNotExist:
            tag = Tag.objects.create(name=name)
        except Tag.MultipleObjectsReturned:
            # TODO: remove this exception branch, when #770 is fixed
            tag = Tag.objects.filter(name__iexact=name).first()
        tag_group, tag_name = get_tag_render_data(name)
        return self.makeTag(
            urls.reverse("tag", args=[tag.slug]),
            tag_name,
            tag_group,
        )

    def makeTag(self, href, label, group_label: str = None):
        link_el = util.etree.Element("a")
        link_el.set("href", href)
        link_el.set("class", "tag")
        hash_el = util.etree.Element("span")
        hash_el.set("class", "tag-hash")
        hash_el.text = "#"
        if group_label:
            link_el.set("data-tag-group-key", group_label.lower())
            group_el = util.etree.Element("span")
            group_el.set("class", "tag-group")
            group_el.append(hash_el)
            # The element tail will be output AFTER the closing tag of the
            # element it’s assigned to. One might intuitively think it
            # should be assigned to the group_el, but that is not the case.
            hash_el.tail = group_label + ":"
            link_el.append(group_el)
        else:
            link_el.append(hash_el)
        label_el = util.etree.Element("span")
        label_el.set("class", "tag-name")
        label_el.text = label
        link_el.append(label_el)
        return link_el


class TagReferenceExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns["tag_reference"] = TagReferencePattern(RE_TAG_REF.pattern, md)


ExtendedLinkPattern.register_extension(TagLinkExtension())
markdown_extensions.append(TagReferenceExtension())
