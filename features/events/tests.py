import re

from content import models as content
import core.tests
from core import tests
from features.associations import models as associations
from features.contributions import models as contributions
import features.gestalten.tests
from features.memberships import test_mixins as memberships
from features.subscriptions import test_mixins as subscriptions


class InternalEventMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content = content.Event.objects.create(
                author=cls.gestalt, time='2000-01-01 12:00+00:00')


class PublicEventMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content = content.Event.objects.create(
                author=cls.gestalt, public=True, time='2000-01-01 12:00+00:00',
                title='Test Event')


# class InternalEventInGroupWithOtherMember(
#         subscriptions.NotificationToOtherGestalt,
#         subscriptions.SenderNameIsGestalt,
#         InternalEventMixin, memberships.OtherMemberMixin,
#         memberships.MemberMixin, tests.Test):
#     """
#     If a group member creates an internal event
#     * a notification to other members should be sent.
#     * the sender name should be mentioned.
#     """


# class InternalEventInGroupWithOtherSubscriber(
#         subscriptions.NotificationToOtherGestalt,
#         InternalEventMixin, subscriptions.OtherGroupSubscriberMixin,
#         memberships.MemberMixin, tests.Test):
#     """
#     If a group member creates an internal event
#     * no notification to subscribers should be sent.
#     """


class PublicEventInGroupWithOtherMember(
        subscriptions.NotificationToOtherGestalt,
        subscriptions.SenderNameIsGestalt,
        PublicEventMixin, memberships.OtherMemberMixin,
        memberships.MemberMixin, tests.Test):
    """
    If a group member creates a public event
    * a notification to other members should be sent.
    * the sender name should be mentioned.
    """


class PublicEventInGroupWithOtherSubscriber(
        subscriptions.NotificationToOtherGestalt,
        subscriptions.SenderIsAnonymous,
        PublicEventMixin, subscriptions.OtherGroupSubscriberMixin,
        memberships.MemberMixin, tests.Test):
    """
    If a group member creates a public event
    * a notification to subscribers should be sent.
    * the sender name should not be mentioned.
    """


class Guest(memberships.MemberMixin, core.tests.Test):
    def create_event(self, **kwargs):
        self.client.force_login(self.gestalt.user)
        kwargs.update({
            'title': 'Test', 'text': 'Test', 'place': 'Test', 'time': '3000-01-01 00:00',
            'until_time': '3000-01-01 00:00'})
        self.client.post(self.get_url('create-event'), kwargs)
        self.client.logout()

    def get_event_url(self):
        return associations.Association.objects.get(content__title='Test').get_absolute_url()

    def create_group_event(self, **kwargs):
        self.client.force_login(self.gestalt.user)
        kwargs.update({
            'title': 'Group Event', 'text': 'Test', 'place': 'Test',
            'time': '3000-01-01 00:00', 'until_time': '3000-01-01 00:00'})
        self.client.post(self.get_url('create-group-event', self.group.slug), kwargs)
        self.client.logout()

    def get_group_event_url(self):
        return associations.Association.objects.get(
                content__title='Group Event').get_absolute_url()

    def test_guest_event_link(self):
        self.assertContainsLink(self.client.get('/'), self.get_url('create-event'))
        self.assertNotContainsLink(
                self.client.get(self.get_url('events')), self.get_url('create-event'))
        self.assertContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_url('create-event'))
        self.assertNotContainsLink(
                self.client.get(self.group.get_absolute_url()), self.get_url('create-event'))

    def test_guest_create_event(self):
        self.assertLogin(url_name='create-event')
        self.assertLogin(url_name='create-event', method='post')

    def test_guest_create_group_event(self):
        self.assertLogin(url_name='create-group-event', url_args=[self.group.slug])
        self.assertLogin(
                url_name='create-group-event', url_args=[self.group.slug], method='post')

    def test_guest_public_event(self):
        self.create_event(public=True)
        self.assertContainsLink(self.client.get('/'), self.get_event_url())
        self.assertContainsLink(
                self.client.get(self.get_url('events')), self.get_event_url())
        self.assertContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_event_url())
        self.assertOk(url=self.get_event_url())

    def test_guest_internal_event(self):
        self.create_event(public=False)
        self.assertNotContainsLink(self.client.get('/'), self.get_event_url())
        self.assertNotContainsLink(
                self.client.get(self.get_url('events')), self.get_event_url())
        self.assertNotContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_event_url())
        self.assertLogin(url=self.get_event_url())

    def test_guest_public_group_event(self):
        self.create_group_event(public=True)
        self.assertContainsLink(obj=self.group, link_url=self.get_group_event_url())
        self.assertOk(url=self.get_group_event_url())
        self.assertLogin(url=self.get_group_event_url(), method='post')

    def test_guest_internal_group_event(self):
        self.create_group_event(public=False)
        self.assertNotContainsLink(obj=self.group, link_url=self.get_group_event_url())
        self.assertLogin(url=self.get_group_event_url())
        self.assertLogin(url=self.get_group_event_url(), method='post')


class Gestalt(memberships.AuthenticatedMemberMixin, core.tests.Test):
    def create_event(self, **kwargs):
        kwargs.update({
            'title': 'Test', 'text': 'Test', 'place': 'Test', 'time': '3000-01-01 00:00',
            'until_time': '3000-01-01 00:00'})
        return self.client.post(self.get_url('create-event'), kwargs)

    def create_group_event(self, **kwargs):
        kwargs.update({
            'title': 'Group Event', 'text': 'Test', 'place': 'Test',
            'time': '3000-01-01 00:00', 'until_time': '3000-01-01 00:00'})
        return self.client.post(self.get_url('create-group-event', self.group.slug), kwargs)

    def get_event_url(self):
        return associations.Association.objects.get(content__title='Test').get_absolute_url()

    def get_group_event_url(self):
        return associations.Association.objects.get(
                content__title='Group Event').get_absolute_url()

    def test_gestalt_event_link(self):
        self.assertContainsLink(self.client.get('/'), self.get_url('create-event'))
        self.assertContainsLink(
                self.client.get(self.get_url('events')), self.get_url('create-event'))
        self.assertContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_url('create-event'))
        self.assertContainsLink(self.client.get(self.group.get_absolute_url()), self.get_url(
            'create-group-event', self.group.slug))

    def test_gestalt_create_event(self):
        self.assertEqual(self.client.get(self.get_url('create-event')).status_code, 200)
        response = self.create_event()
        self.assertRedirects(response, self.get_event_url())
        self.assertExists(associations.Association, content__title='Test')

    def test_gestalt_create_group_event(self):
        self.assertEqual(self.client.get(self.get_url(
            'create-group-event', self.group.slug)).status_code, 200)
        response = self.create_group_event()
        self.assertRedirects(response, self.get_group_event_url())
        self.assertExists(associations.Association, content__title='Group Event')

    def test_gestalt_public_event(self):
        self.create_event(public=True)
        self.assertContainsLink(self.client.get('/'), self.get_event_url())
        self.assertContainsLink(
                self.client.get(self.get_url('events')), self.get_event_url())
        self.assertContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_event_url())
        self.assertOk(url=self.get_event_url())

    def test_gestalt_internal_event(self):
        self.create_event(public=False)
        self.assertContainsLink(self.client.get('/'), self.get_event_url())
        self.assertContainsLink(
                self.client.get(self.get_url('events')), self.get_event_url())
        self.assertContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_event_url())
        self.assertOk(url=self.get_event_url())

    def test_gestalt_public_group_event(self):
        self.create_group_event(public=True)
        self.assertContainsLink(obj=self.group, link_url=self.get_group_event_url())
        self.assertOk(url=self.get_group_event_url())

    def test_gestalt_internal_group_event(self):
        self.create_group_event(public=False)
        self.assertContainsLink(obj=self.group, link_url=self.get_group_event_url())
        self.assertOk(url=self.get_group_event_url())

    def test_gestalt_comment_event(self):
        self.create_event()
        self.assertRedirect(
                url=self.get_event_url(), method='post', data={'text': 'Comment'})
        self.assertExists(contributions.Contribution, text__text='Comment')


class GroupCalendarExportMember(memberships.AuthenticatedMemberMixin,
                                features.gestalten.tests.OtherGestaltMixin,
                                tests.Test):

    def test_access_private_calendar(self):
        """ test the (in)accessibility of a private calendar of a group for a logged in member """
        data = self.client.get(self.get_url('group-events-export', (self.group.slug, )))
        private_url_regex = re.compile(r'>(?P<url>[^<]+/private.ics[^<]+)<')
        match = private_url_regex.search(data.content.decode('utf8'))
        self.assertTrue(match)
        private_url = match.groupdict()['url']
        self.assertTrue("token" in private_url)
        # verify access via the private URL
        data = self.client.get(private_url)
        self.assertTrue('BEGIN:VCALENDAR' in data.content.decode('utf8'))
        # verify rejected access with a wrong private URL
        data = self.client.get(private_url + 'foo')
        self.assertEqual(data.status_code, 401)
        # verify rejected access with missing query arguments
        url_without_token = private_url.split("?")[0]
        self.assertNotEqual(url_without_token, private_url)
        data = self.client.get(url_without_token)
        self.assertEqual(data.status_code, 401)
        # verify rejected access with wrong username within token
        # assemble a new URL by replacing the username within the token
        wrong_user_url = '{}?{}:{}'.format(private_url.split('?')[0],
                                           self.other_gestalt.user.username,
                                           private_url.split(':')[-1])
        self.assertNotEqual(wrong_user_url, private_url)
        data = self.client.get(wrong_user_url)
        self.assertEqual(data.status_code, 401)

    def test_access_public_calendar(self):
        """ test the accessibility of a public calendar of a group for a logged in member """
        data = self.client.get(self.get_url('group-events-export', (self.group.slug, )))
        public_url_regex = re.compile(r'>(?P<url>[^<]+/public.ics[^<]*)<')
        match = public_url_regex.search(data.content.decode('utf8'))
        self.assertTrue(match)
        public_url = match.groupdict()['url']
        data = self.client.get(public_url)
        self.assertTrue('BEGIN:VCALENDAR' in data.content.decode('utf8'))


class GroupCalendarExportNonMember(memberships.MemberMixin,
                                   features.gestalten.tests.OtherAuthenticatedMixin,
                                   tests.Test):

    def test_rejected_access_private_calendar(self):
        """ test the inaccessibility of a private calendar for a logged in non-member """
        data = self.client.get(self.get_url('group-events-export', (self.group.slug, )))
        private_url_regex = re.compile(r'>(?P<url>[^<]+/private.ics[^<]*)<')
        match = private_url_regex.search(data.content.decode('utf8'))
        # the private URL should not be displayed
        self.assertIsNone(match)


class GestaltCalendarExport(features.gestalten.tests.AuthenticatedMixin, tests.Test):

    def test_access_private_calendar(self):
        """ test the (in)accessibility of a private calendar of a gestalt itself while being
        logged in

        TODO: this is a code copy from GroupCalendarExportMember - merge these!
        """
        data = self.client.get(self.get_url('gestalt-events-export',
                                            (self.gestalt.user.username, )))
        private_url_regex = re.compile(r'>(?P<url>[^<]+/private.ics[^<]+)<')
        match = private_url_regex.search(data.content.decode('utf8'))
        self.assertTrue(match)
        private_url = match.groupdict()['url']
        self.assertTrue("token" in private_url)
        # verify access via the private URL
        data = self.client.get(private_url)
        self.assertTrue('BEGIN:VCALENDAR' in data.content.decode('utf8'))
        # verify rejected access with a wrong private URL
        data = self.client.get(private_url + 'foo')
        self.assertEqual(data.status_code, 401)
        # verify rejected access with missing query arguments
        url_without_token = private_url.split("?")[0]
        self.assertNotEqual(url_without_token, private_url)
        data = self.client.get(url_without_token)
        self.assertEqual(data.status_code, 401)
        # verify rejected access with wrong username within token
        # assemble a new URL by replacing the username within the token
        wrong_user_url = '{}?{}:{}'.format(private_url.split('?')[0],
                                           self.other_gestalt.user.username,
                                           private_url.split(':')[-1])
        self.assertNotEqual(wrong_user_url, private_url)
        data = self.client.get(wrong_user_url)
        self.assertEqual(data.status_code, 401)
