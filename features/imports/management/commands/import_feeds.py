import datetime
import re
import time

import django
import feedparser
import requests

import core
from features.associations import models as associations
from features.content import models as content
from features.gestalten import models as gestalten
from features.groups import models as groups
from features.imports import models


class Command(django.core.management.base.BaseCommand):

    FEED_RE = r'<link [^>]*type=\"application/(?:rss|atom)\+xml\" [^>]*href=\"([^\"]+)\"[^>]*>'

    def handle(self, *args, **options):
        author = gestalten.Gestalt.objects.get(id=django.conf.settings.IMPORTER_ID)
        for group in groups.Group.objects.filter(url_import_feed=True):
            r = requests.get(group.url)
            m = re.search(self.FEED_RE, r.text)
            if m:
                feed_url = m.group(1)
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    key = entry.get('id', entry.get('link'))
                    if key and not models.Imported.objects.filter(key=key).exists():
                        title = entry.get('title')
                        text = entry.get('summary')
                        if title and text:
                            c = content.Content.objects.create(title=title)
                            link = entry.get('link')
                            if link:
                                text = '{}\n\n{}'.format(text, link)
                            v = content.Version.objects.create(
                                    author=author, content=c, text=text)
                            t = entry.get('published_parsed')
                            if t:
                                t = datetime.datetime.fromtimestamp(time.mktime(t))
                                tz = django.utils.timezone.get_current_timezone()
                                v.time_created = tz.localize(t)
                                v.save()
                            slug = core.models.get_unique_slug(
                                    associations.Association, {
                                        'entity_id': group.id,
                                        'entity_type': group.content_type,
                                        'slug': core.text.slugify(title),
                                        })
                            associations.Association.objects.create(
                                    entity_type=group.content_type, entity_id=group.id,
                                    container_type=c.content_type, container_id=c.id,
                                    public=True, slug=slug)
                            models.Imported.objects.create(key=key)
