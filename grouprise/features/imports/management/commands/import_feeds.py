import datetime
import logging
import re
import sys
import time
import urllib.request

import django
import feedparser
from django.conf import settings

import grouprise.core
from grouprise.core.templatetags.defaultfilters import html2text
from grouprise.core.utils import slugify
from grouprise.features.associations import models as associations
from grouprise.features.content import models as content
from grouprise.features.content.signals import post_create
from grouprise.features.gestalten import models as gestalten
from grouprise.features.groups import models as groups
from grouprise.features.imports import models


logger = logging.getLogger(__name__)

FEED_RE = re.compile(
        br'<link\s+[^>]*'
        br'(?:type=[\"\']application/(?:rss|atom)\+xml[\"\']\s+[^>]*'
        br'href=[\"\']([^\"\']+)[\"\']'
        br'|href=[\"\']([^\"\']+)[\"\']\s+[^>]*'
        br'type=[\"\']application/(?:rss|atom)\+xml[\"\'])'
        br'[^>]*>')


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
        key = entry.get('id')
        if not key:
            key = entry.get('link')
        if key and not models.Imported.objects.filter(key=key).exists():
            title = entry.get('title')
            text = html2text(entry.get('summary'), preset='import')
            if title and text:
                c = content.Content.objects.create(title=title)
                link = entry.get('link')
                if link:
                    text = '{}\n\n{}'.format(text, link)
                v = content.Version.objects.create(author=submitter, content=c, text=text)
                t = entry.get('published_parsed')
                if t:
                    t = datetime.datetime.fromtimestamp(time.mktime(t))
                    tz = django.utils.timezone.get_current_timezone()
                    v.time_created = tz.localize(t)
                    v.save()
                slug = grouprise.core.models.get_unique_slug(
                        associations.Association, {
                            'entity_id': target_group.id,
                            'entity_type': target_group.content_type,
                            'slug': slugify(title),
                            })
                associations.Association.objects.create(
                        entity_type=target_group.content_type, entity_id=target_group.id,
                        container_type=c.content_type, container_id=c.id,
                        public=True, slug=slug)
                models.Imported.objects.create(key=key)
                post_create.send(sender=Command, instance=c)


class Command(django.core.management.base.BaseCommand):

    def handle(self, *args, **options):
        feed_importer_id = settings.GROUPRISE.get('FEED_IMPORTER_GESTALT_ID')
        if feed_importer_id is None:
            logger.error(
                    "No FEED_IMPORTER_GESTALT_ID setting is specified - aborting feed import.")
            sys.exit(1)
        author = gestalten.Gestalt.objects.get(id=feed_importer_id)
        for group in groups.Group.objects.filter(url_import_feed=True):
            if group.url:
                request = urllib.request.Request(group.url, headers={"User-Agent": "grouprise"})
                try:
                    with urllib.request.urlopen(request) as req:
                        text = req.read()
                except urllib.request.URLError as exc:
                    logger.warning(f"Failed to retrieve content from '{group.url}': {exc}")
                else:
                    feed_url = parse_feed_url_from_website_content(text)
                    logger.info(f"Retrieved feed URL for group '{group.name}': {feed_url}")
                    if feed_url:
                        import_from_feed(feed_url, author, group)
            else:
                logger.warning(
                    "Skipping feed import due to missing source URL for group '%s'", group)
