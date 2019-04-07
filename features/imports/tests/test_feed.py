import datetime

from django.conf import settings
import django.utils.timezone

from core import tests
from features.associations import models as associations
from features.memberships.test_mixins import MemberMixin, OtherMemberMixin
from ..management.commands.import_feeds import (
    import_from_feed, parse_feed_url_from_website_content)


FEED_LINK_EXAMPLES = (
    ('<link rel="alternate" type="application/rss+xml" title="Peter Weiss Haus &raquo; Feed" '
     'href="https://peterweisshaus.de/feed/" />"', 'https://peterweisshaus.de/feed/'),
)

FEED_CONTENT_TEMPLATE = (
    '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0">'
    '<channel><title>Channel Title</title><link>https://example.org</link>'
    '<item><title>{title}</title><link>{url}</link><pubDate>{date}</pubDate>'
    '<description>{description}</description><content>Some Content</content>'
    '</item></channel></rss>')


class DetectFeedURL(tests.Test):

    def test_references(self):
        for snippet, feed_url in FEED_LINK_EXAMPLES:
            with self.subTest(feed_url=feed_url):
                self.assertEqual(parse_feed_url_from_website_content(snippet), feed_url)


class ImportFeedItems(MemberMixin, OtherMemberMixin, tests.Test):

    FEED_DEFAULTS = {
        "title": "First Title", "url": "https://example.org/1/2",
        "date": "Tue, 05 Jun 2018 07:55:15 +0000", "description": "Some Description",
        "content": "Some Content",
    }

    def setUp(self):
        super().setUp()
        settings.GROUPRISE["FEED_IMPORTER_GESTALT_ID"] = self.other_gestalt.id

    def _get_now(self):
        tz = django.utils.timezone.get_current_timezone()
        return datetime.datetime.now(tz=tz)

    def _get_feed_content(self, **kwargs):
        data = dict(self.FEED_DEFAULTS)
        data.update(kwargs)
        if "date" not in data:
            data["date"] = self._get_now()
        if isinstance(data["date"], datetime.datetime):
            data["date"] = data["date"].strftime("%a, %d %b %Y %H:%M:%S %z").strip()
        return FEED_CONTENT_TEMPLATE.format(**data)

    def test_content(self):
        now = self._get_now()
        import_from_feed(self._get_feed_content(date=now), self.gestalt, self.group)
        # TODO: check timezone correctness ("hour" is omitted below)
        self.assertExists(
            associations.Association,
            content__title="First Title",
            content__versions__time_created__year=now.year,
            content__versions__time_created__month=now.month,
            content__versions__time_created__day=now.day,
            content__versions__time_created__minute=now.minute,
            content__versions__time_created__second=now.second,
        )

    def test_ignore_duplicates(self):
        import_from_feed(self._get_feed_content(), self.gestalt, self.group)
        self.assertEqual(associations.Association.objects.count(), 1)
        import_from_feed(self._get_feed_content(), self.gestalt, self.group)
        self.assertEqual(associations.Association.objects.count(), 1)
