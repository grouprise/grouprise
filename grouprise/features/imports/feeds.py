import datetime
import logging
import re
import urllib.request

import django
from django.utils.translation import gettext as _
import feedparser

import grouprise.core
from grouprise.core.settings import CORE_SETTINGS
from grouprise.core.signals import post_create
from grouprise.core.templatetags.defaultfilters import html2text
from grouprise.core.utils import slugify
from grouprise.features.associations import models as associations
from grouprise.features.content import models as content
from grouprise.features.gestalten import models as gestalten
from grouprise.features.groups import models as groups
from grouprise.features.imports import models

FEED_RE = re.compile(
    rb"<link\s+[^>]*"
    rb"(?:type=[\"\']application/(?:rss|atom)\+xml[\"\']\s+[^>]*"
    rb"href=[\"\']([^\"\']+)[\"\']"
    rb"|href=[\"\']([^\"\']+)[\"\']\s+[^>]*"
    rb"type=[\"\']application/(?:rss|atom)\+xml[\"\'])"
    rb"[^>]*>"
)

logger = logging.getLogger(__name__)


def parse_feed_url_from_website_content(raw_website_content):
    for match_groups in FEED_RE.findall(raw_website_content):
        feed_url = match_groups[0] or match_groups[1]
        if feed_url:
            return feed_url.decode()
    else:
        return None


def import_from_feed(feed_url, submitter, target_group):
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        key = entry.get("id")
        if not key:
            key = entry.get("link")
        if key and not models.Imported.objects.filter(key=key).exists():
            title = entry.get("title")
            text = html2text(entry.get("summary"), preset="import")
            if title and text:
                c = content.Content.objects.create(title=title)
                link = entry.get("link")
                if link and link not in text:
                    link_caption = _("Proceed to article")
                    text = f"{text}\n\n[{link_caption}]({link})"
                v = content.Version.objects.create(
                    author=submitter, content=c, text=text
                )
                t = entry.get("published_parsed")
                if t:
                    tz = django.utils.timezone.get_current_timezone()
                    v.time_created = datetime.datetime.now(tz=tz)
                    v.save()
                slug = grouprise.core.models.get_unique_slug(
                    associations.Association,
                    {
                        "entity_id": target_group.id,
                        "entity_type": target_group.content_type,
                        "slug": slugify(title),
                    },
                )
                associations.Association.objects.create(
                    entity_type=target_group.content_type,
                    entity_id=target_group.id,
                    container_type=c.content_type,
                    container_id=c.id,
                    public=True,
                    slug=slug,
                )
                models.Imported.objects.create(key=key)
                post_create.send(sender=None, instance=c)


def run_feed_import_for_groups():
    processed_feeds = []
    if CORE_SETTINGS.FEED_IMPORTER_GESTALT_ID is not None:
        author = gestalten.Gestalt.objects.get(
            id=CORE_SETTINGS.FEED_IMPORTER_GESTALT_ID
        )
        for group in groups.Group.objects.filter(url_import_feed=True):
            if group.url:
                request = urllib.request.Request(
                    group.url, headers={"User-Agent": "grouprise"}
                )
                try:
                    with urllib.request.urlopen(request) as req:
                        text = req.read()
                except OSError as exc:
                    logger.warning(
                        f"Failed to retrieve content from '{group.url}': {exc}"
                    )
                else:
                    feed_url = parse_feed_url_from_website_content(text)
                    logger.info(
                        f"Retrieved feed URL for group '{group.name}': {feed_url}"
                    )
                    if feed_url:
                        import_from_feed(feed_url, author, group)
                        processed_feeds.append(group)
            else:
                logger.warning(
                    "Skipping feed import due to missing source URL for group '%s'",
                    group,
                )
        return processed_feeds
    else:
        logger.error(
            "No FEED_IMPORTER_GESTALT_ID setting is specified - aborting feed import."
        )
        return None
