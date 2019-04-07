import datetime
import re
import ssl
import time

import django
import feedparser
import requests
from django.conf import settings

import core
from core.templatetags.core import html2text
from features.associations import models as associations
from features.content import models as content
from features.content.signals import post_create
from features.gestalten import models as gestalten
from features.groups import models as groups
from features.imports import models


FEED_RE = (
        r'<link\s+[^>]*'
        r'(?:type=[\"\']application/(?:rss|atom)\+xml[\"\']\s+[^>]*'
        r'href=[\"\']([^\"\']+)[\"\']'
        r'|href=[\"\']([^\"\']+)[\"\']\s+[^>]*'
        r'type=[\"\']application/(?:rss|atom)\+xml[\"\'])'
        r'[^>]*>')


if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


def parse_feed_url_from_website_content(website_content):
    matches = re.findall(FEED_RE, website_content)
    for i, match_groups in enumerate(matches):
        feed_url = match_groups[0] or match_groups[1]
        if feed_url:
            return feed_url
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
                slug = core.models.get_unique_slug(
                        associations.Association, {
                            'entity_id': target_group.id,
                            'entity_type': target_group.content_type,
                            'slug': core.text.slugify(title),
                            })
                associations.Association.objects.create(
                        entity_type=target_group.content_type, entity_id=target_group.id,
                        container_type=c.content_type, container_id=c.id,
                        public=True, slug=slug)
                models.Imported.objects.create(key=key)
                post_create.send(sender=Command, instance=c)


class Command(django.core.management.base.BaseCommand):

    def handle(self, *args, **options):
        author = gestalten.Gestalt.objects.get(
            id=settings.GROUPRISE.get('FEED_IMPORTER_GESTALT_ID'))
        for group in groups.Group.objects.filter(url_import_feed=True):
            try:
                response = requests.get(group.url, headers={'User-Agent': 'grouprise'})
            except (requests.exceptions.ChunkedEncodingError,
                    requests.exceptions.ConnectionError):
                pass
            else:
                feed_url = parse_feed_url_from_website_content(response.text)
                if feed_url:
                    import_from_feed(feed_url, author, group)
