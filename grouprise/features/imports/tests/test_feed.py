import datetime

import django.utils.timezone

from grouprise.core import tests
from grouprise.core.tests import temporary_settings_override
from grouprise.features.associations import models as associations
from grouprise.features.memberships.test_mixins import MemberMixin, OtherMemberMixin
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

    def _get_now(self):
        tz = django.utils.timezone.get_current_timezone()
        # remove microseconds, since sqlite uses stores only seconds
        return datetime.datetime.now(tz=tz).replace(microsecond=0)

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
        # compare date and time (timezone aware) separately in order to ignore different timezones
        now_utc = now.astimezone(datetime.timezone.utc)
        self.assertExists(
            associations.Association,
            content__title="First Title",
            content__versions__time_created__date=now_utc.date(),
            content__versions__time_created__time=now_utc.time(),
        )

    def test_ignore_duplicates(self):
        import_from_feed(self._get_feed_content(), self.gestalt, self.group)
        self.assertEqual(associations.Association.objects.count(), 1)
        import_from_feed(self._get_feed_content(), self.gestalt, self.group)
        self.assertEqual(associations.Association.objects.count(), 1)

    def test_notifications_all(self):
        with temporary_settings_override("FEED_IMPORTER_GESTALT_ID", self.other_gestalt.id):
            self.assertEqual(associations.Association.objects.count(), 0)
            # send a "new" (recent date) feed entry: otherwise its notification is skipped
            import_from_feed(self._get_feed_content(date=self._get_now()),
                             self.gestalt, self.group)
            self.assertEqual(associations.Association.objects.count(), 1)
            self.assertNotificationRecipient(self.gestalt)
            # the "other_gestalt" receives no notifications (see FEED_IMPORTER_GESTALT_ID)
            self.assertNotNotificationRecipient(self.other_gestalt)
            self.assertNotificationsSent(1)
