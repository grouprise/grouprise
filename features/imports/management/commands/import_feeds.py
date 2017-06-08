import re

import django
import feedparser
import requests

from features.groups import models as groups


class Command(django.core.management.base.BaseCommand):

    FEED_RE = r'<link [^>]*type=\"application/(?:rss|atom)\+xml\" [^>]*href=\"([^\"]+)\"[^>]*>'
    
    def handle(self, *args, **options):
        for group in groups.Group.objects.filter(url_import_feed=True):
            r = requests.get(group.url)
            m = re.search(self.FEED_RE, r.text)
            if m:
                feed_url = m.group(1)
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    key = entry.get('id', entry.get('link'))
                    if key:
                        print(key)
