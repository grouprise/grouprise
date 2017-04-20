import core.tests
from content import models as content
from core import tests
from features.associations import models as associations
from features.contributions import models as contributions
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
