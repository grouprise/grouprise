"""
This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.
"""

from . import filters, models
from entities import models as entities
from features.content import tests as content
from features.gestalten import tests as gestalten
from features.groups import tests as groups
from features.memberships import test_mixins as memberships


class ContentSubscribedMixin(content.NoAuthorContentMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Subscription.objects.create(
                subscribed_to=cls.content, subscriber=cls.gestalt)


class GroupSubscribedMixin(gestalten.AuthenticatedMixin, groups.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Subscription.objects.create(
                subscribed_to=cls.group, subscriber=cls.gestalt)


class OtherContentSubscriberMixin(
        content.ContentMixin, gestalten.OtherGestaltMixin, groups.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Subscription.objects.create(
                subscribed_to=cls.content,
                subscriber=cls.other_gestalt)


class OtherGroupSubscriberMixin(
        gestalten.OtherGestaltMixin, groups.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Subscription.objects.create(
                subscribed_to=cls.group,
                subscriber=cls.other_gestalt)


class AllContentUnsubscribedMixin(memberships.MemberMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        s = models.Subscription.objects.create(
                subscribed_to=cls.group, subscriber=cls.gestalt, unsubscribe=True)
        models.Filter.objects.create(
                filter_id=filters.all_content.filter_id, subscription=s)


class ExternalUnsubscribedMixin(memberships.MemberMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        s = models.Subscription.objects.create(
                subscribed_to=cls.group, subscriber=cls.gestalt, unsubscribe=True)
        models.Filter.objects.create(
                filter_id=filters.initial_author_no_member.filter_id, subscription=s)


class NoNotificationToOtherGestalt:
    def test_associate_content(self):
        entities.GroupContent.objects.create(
                content=self.content, group=self.group)
        self.assertNoNotificationSent()


class NotificationToOtherGestalt:
    def test_associate_content(self):
        entities.GroupContent.objects.create(
                content=self.content, group=self.group)
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.other_gestalt)


class SenderIsAnonymous:
    def test_sender_name(self):
        entities.GroupContent.objects.create(
                content=self.content, group=self.group)
        self.assertNotificationSenderAnonymous()


class SenderNameIsGestalt:
    def test_sender_name(self):
        entities.GroupContent.objects.create(
                content=self.content, group=self.group)
        self.assertNotificationSenderName(self.gestalt)
