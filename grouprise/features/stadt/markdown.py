import re
import typing

import xml.etree.ElementTree as etree
from django.db.models import Q
from markdown import Extension, inlinepatterns, util

from grouprise.core.markdown import ExtendedLinkPattern, markdown_extensions
from grouprise.core.templatetags.defaultfilters import full_url
from grouprise.features.associations import models as associations
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups.models import Group

from . import RE_CONTENT_REF


class UnknownEntityError(KeyError):
    """the entity (gestalt or group) was not found"""


class UnknownContentError(KeyError):
    """the piece of content was not found"""


def _make_link_tag(url, title, text) -> etree.Element:
    el = etree.Element("a")
    el.set("href", url)
    el.set("title", title)
    el.text = text
    return el


def _get_entity_by_slug_with_relaxed_case(wanted_slug: str):
    """try to find the entity with an exact slug match and fall back to a case insensitive match

    Raises the `KeyError` if the entity does not exist.
    """
    for model, field_query in (
        (Group, "slug"),
        (Gestalt, "user__username"),
        (Group, "slug__iexact"),
        (Gestalt, "user__username__iexact"),
    ):
        try:
            return model.objects.get(**{field_query: wanted_slug})
        except model.DoesNotExist:
            pass
    raise KeyError(f"Entity does not exist: {wanted_slug}")


def _parse_tag_from_entity_or_content(
    entity_slug: str, content_slug: typing.Optional[str] = None
) -> etree.Element:
    """create an HTML tag for a given reference based on a regex match

    Raises UnknownEntityError is the given entity does not exist.
    Raises UnknownContentError if the content belonging to the entity does not exist.
    """
    # resolve the entity separately (for a precise exception in case of failure)
    try:
        entity = _get_entity_by_slug_with_relaxed_case(entity_slug)
    except KeyError:
        # the entity does not exist
        raise UnknownEntityError()
    if content_slug:
        # the link refers to an association
        if isinstance(entity, Gestalt):
            entity_query = Q(gestalt=entity)
        else:
            entity_query = Q(group=entity)
        try:
            association = associations.Association.objects.get(
                entity_query, slug=content_slug
            )
            name = "@{}/{}".format(entity_slug, content_slug)
        except associations.Association.DoesNotExist:
            raise UnknownContentError()
        else:
            return get_association_link(association, name)
    else:
        # we are dealing with an entity (not an association)
        return get_entity_link(entity)


def get_entity_link(entity: typing.Union[Gestalt, Group]) -> etree.Element:
    """generate an ElementTree item referencing an entity"""
    entity_tag = _make_link_tag(
        full_url(entity.get_absolute_url()), str(entity), "@" + entity.slug
    )
    if entity.is_group:
        entity_tag.set("data-component", "grouplink")
        entity_tag.set("data-grouplink-ref", str(entity.id))
    else:
        entity_tag.set("data-component", "gestaltlink")
        entity_tag.set("data-gestaltlink-ref", str(entity.id))
    return entity_tag


def get_association_link(
    association: associations.Association, label: str
) -> etree.Element:
    """generate an ElementTree item referencing an association"""
    return _make_link_tag(
        full_url(association.get_absolute_url()), str(association), label
    )


def get_entity_placeholder(slug):
    el = etree.Element("span")
    el.text = util.AtomicString(f"@{slug} (unbekannte Gruppe/Gestalt)")
    return el


def get_content_placeholder(entity_slug, content_slug):
    el = etree.Element("span")
    span_entity = etree.SubElement(el, "span")
    # the entity link will be resolved in a later cycle
    span_entity.text = f"@{entity_slug}"
    span_entity.tail = util.AtomicString(f"/{content_slug} (Inhalt nicht gefunden)")
    return el


class EntityLinkExtension:
    """allow entity links in URLs, e.g. `see [group 'foo'](@foo)`"""

    def process_link(self, a):
        el_href = a.get("href")
        href_match = re.match(RE_CONTENT_REF, el_href)
        if href_match:
            entity_slug = href_match.group(1).lstrip("@")
            content_slug = href_match.group(2)
            try:
                generated_tag = _parse_tag_from_entity_or_content(
                    entity_slug, content_slug
                )
            except UnknownEntityError:
                return get_entity_placeholder(entity_slug)
            except UnknownContentError:
                return get_content_placeholder(entity_slug, content_slug)
            else:
                # transfer attributes from the generated tag to the existing link
                for attribute in (
                    "data-component",
                    "data-gestaltlink-ref",
                    "data-grouplink-ref",
                    "href",
                    "title",
                ):
                    value = generated_tag.get(attribute)
                    if value:
                        a.set(attribute, value)
                return a
        else:
            # the link is probably just a real URL
            return a


ExtendedLinkPattern.register_extension(EntityLinkExtension())


class ContentReferencePattern(inlinepatterns.ReferenceInlineProcessor):
    """substitute content links, e.g. `@foo` or `@foo/bar`"""

    def handleMatch(self, m, data):
        entity_slug = m.group(1).lstrip("@")
        content_slug = m.group(2)
        try:
            html_tag = _parse_tag_from_entity_or_content(entity_slug, content_slug)
        except UnknownEntityError:
            html_tag = get_entity_placeholder(entity_slug)
        except UnknownContentError:
            html_tag = get_content_placeholder(entity_slug, content_slug)
        return (html_tag, *m.span())


class ContentReferenceExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            ContentReferencePattern(RE_CONTENT_REF.pattern, md),
            "content_reference",
            # the MagiclinkMailPattern is registered for 84.9 - we are less relevant
            70,
        )


markdown_extensions.append(ContentReferenceExtension())
