import re

import django

import core
import features
from core import tests
from features.associations import models as associations
from features.contributions import models as contributions
from features.memberships import test_mixins as memberships


def _get_adjusted_event_args(missing_keys=None, **kwargs):
    """ assemble a dictionary of arguments for a new event

    @param missing_keys: keys to be removed from the dictionary
    other keyword arguments: values to be overriden in the default dictionary
    """
    event_args = {'title': 'Some Event', 'text': 'Test Text', 'place': 'Test Place',
                  'time': '3000-01-01 00:00', 'until_time': '3000-01-01 00:00'}
    event_args.update(kwargs)
    for key in (missing_keys or []):
        event_args.pop(key)
    return event_args


class Guest(memberships.MemberMixin, core.tests.Test):

    def create_event(self, **kwargs):
        self.client.force_login(self.gestalt.user)
        self.client.post(self.get_url('create-event'), _get_adjusted_event_args(**kwargs))
        self.client.logout()

    def get_event_url(self, title):
        return associations.Association.objects.get(content__title=title).get_absolute_url()

    def create_group_event(self, **kwargs):
        self.client.force_login(self.gestalt.user)
        self.client.post(self.get_url('create-group-event', self.group.slug),
                         _get_adjusted_event_args(**kwargs))
        self.client.logout()

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
        self.create_event(public=True, title='A public Guest Event')
        event_url = self.get_event_url('A public Guest Event')
        self.assertContainsLink(self.client.get('/'), event_url)
        self.assertContainsLink(self.client.get(self.get_url('events')), event_url)
        self.assertContainsLink(self.client.get(self.gestalt.get_absolute_url()), event_url)
        self.assertOk(url=event_url)

    def test_guest_internal_event(self):
        self.create_event(public=False, title='An internal Guest Event')
        event_url = self.get_event_url('An internal Guest Event')
        self.assertNotContainsLink(self.client.get('/'), event_url)
        self.assertNotContainsLink(self.client.get(self.get_url('events')), event_url)
        self.assertNotContainsLink(self.client.get(self.gestalt.get_absolute_url()), event_url)
        self.assertLogin(url=event_url)

    def test_guest_public_group_event(self):
        self.create_group_event(public=True, title='A public Group Guest Event')
        event_url = self.get_event_url('A public Group Guest Event')
        self.assertContainsLink(obj=self.group, link_url=event_url)
        self.assertOk(url=event_url)
        self.assertLogin(url=event_url, method='post')

    def test_guest_internal_group_event(self):
        self.create_group_event(public=False, title='An internal Group Guest Event')
        event_url = self.get_event_url('An internal Group Guest Event')
        self.assertNotContainsLink(obj=self.group, link_url=event_url)
        self.assertLogin(url=event_url)
        self.assertLogin(url=event_url, method='post')


class Gestalt(memberships.AuthenticatedMemberMixin, core.tests.Test):

    def create_event(self, **kwargs):
        return self.client.post(self.get_url('create-event'), _get_adjusted_event_args(**kwargs))

    def create_group_event(self, **kwargs):
        return self.client.post(self.get_url('create-group-event', self.group.slug),
                                _get_adjusted_event_args(**kwargs))

    def get_event_url(self, title):
        return associations.Association.objects.get(content__title=title).get_absolute_url()

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
        title = 'A new Event'
        response = self.create_event(title=title)
        self.assertRedirects(response, self.get_event_url(title))
        self.assertExists(associations.Association, content__title=title)

    def test_gestalt_create_group_event(self):
        title = 'A new Group Event'
        self.assertEqual(self.client.get(self.get_url(
            'create-group-event', self.group.slug)).status_code, 200)
        response = self.create_group_event(title=title)
        self.assertRedirects(response, self.get_event_url(title))
        self.assertExists(associations.Association, content__title=title)

    def test_gestalt_public_event(self):
        self.create_event(public=True, title='Gestalt Public Event')
        event_url = self.get_event_url('Gestalt Public Event')
        self.assertContainsLink(self.client.get('/'), event_url)
        self.assertContainsLink(self.client.get(self.get_url('events')), event_url)
        self.assertContainsLink(self.client.get(self.gestalt.get_absolute_url()), event_url)
        self.assertOk(url=event_url)

    def test_gestalt_internal_event(self):
        self.create_event(public=False, title='Gestalt Internal Event')
        event_url = self.get_event_url('Gestalt Internal Event')
        self.assertContainsLink(self.client.get('/'), event_url)
        self.assertContainsLink(self.client.get(self.get_url('events')), event_url)
        self.assertContainsLink(self.client.get(self.gestalt.get_absolute_url()), event_url)
        self.assertOk(url=event_url)

    def test_gestalt_public_group_event(self):
        title = 'Public Group Event'
        self.create_group_event(public=True, title=title)
        self.assertContainsLink(obj=self.group, link_url=self.get_event_url(title))
        self.assertOk(url=self.get_event_url(title))

    def test_gestalt_internal_group_event(self):
        self.create_group_event(public=False, title='Gestalt Internal Group Event')
        event_url = self.get_event_url('Gestalt Internal Group Event')
        self.assertContainsLink(obj=self.group, link_url=event_url)
        self.assertOk(url=event_url)

    def test_gestalt_comment_event(self):
        self.create_event(title='Gestalt Comment Event')
        self.assertRedirect(url=self.get_event_url('Gestalt Comment Event'), method='post',
                            data={'text': 'Comment'})
        self.assertExists(contributions.Contribution, text__text='Comment')


class TwoGestalten(
        memberships.OtherMemberMixin, memberships.AuthenticatedMemberMixin, core.tests.Test):

    def create_event(self, **kwargs):
        event_args = _get_adjusted_event_args(**kwargs)
        self.client.post(self.get_url('create-group-event', self.group.slug), event_args)
        self.association = associations.Association.objects.get(content__title=event_args['title'])

    def get_content_url(self):
        return self.get_url('content', (self.association.entity.slug, self.association.slug))

    def get_perma_url(self):
        return self.get_url('content-permalink', (self.association.pk))

    def test_event_notified(self):
        self.create_event(text='My Text', place='My Place')
        self.assertNotificationsSent(2)
        self.assertNotificationRecipient(self.gestalt)
        self.assertNotificationRecipient(self.other_gestalt)
        self.assertNotificationContains(self.get_perma_url())
        self.assertNotificationContains('My Text')
        self.assertNotificationContains('My Place')


class GroupCalendarExportMember(memberships.AuthenticatedMemberMixin,
                                features.gestalten.tests.OtherGestaltMixin,
                                tests.Test):

    def create_group_event(self, **kwargs):
        count_before = associations.Association.objects.count()
        self.client.post(self.get_url('create-group-event', self.group.slug),
                         _get_adjusted_event_args(**kwargs))
        count_after = associations.Association.objects.count()
        # verify that exactly one item was added
        self.assertEqual(count_before + 1, count_after, "Failed to create item: {}".format(kwargs))

    def get_calendar_export_url(self, is_public):
        data = self.client.get(self.get_url('group-events-export', (self.group.slug, )))
        if is_public:
            url_regex = re.compile(r'>(?P<url>[^<]+/public.ics[^<]*)<')
        else:
            url_regex = re.compile(r'>(?P<url>[^<]+/private.ics[^<]+)<')
        match = url_regex.search(data.content.decode('utf8'))
        self.assertTrue(match)
        calendar_export_url = match.groupdict()['url']
        if is_public:
            self.assertNotIn("token", calendar_export_url)
        else:
            self.assertIn("token", calendar_export_url)
        return calendar_export_url

    def test_private_public_calendar_content(self):
        """ verify that private and public events are only available in their calendars """
        # create a private and a public event
        self.create_group_event(title='Private Event', public=False)
        self.create_group_event(title='Public Event', public=True)
        # verify the content of the private calendar
        calendar_url = self.get_calendar_export_url(False)
        data = self.client.get(calendar_url).content.decode('utf8')
        self.assertIn('BEGIN:VCALENDAR', data)
        self.assertIn('Private Event', data)
        self.assertNotIn('Public Event', data)
        # verify the content of the public calendar
        calendar_url = self.get_calendar_export_url(True)
        data = self.client.get(calendar_url).content.decode('utf8')
        self.assertIn('BEGIN:VCALENDAR', data)
        self.assertNotIn('Private Event', data)
        self.assertIn('Public Event', data)

    def test_access_private_calendar(self):
        """ test the (in)accessibility of a private calendar of a group for a logged in member """
        private_url = self.get_calendar_export_url(False)
        # verify access via the private URL
        data = self.client.get(private_url)
        self.assertIn('BEGIN:VCALENDAR', data.content.decode('utf8'))
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
        public_url = self.get_calendar_export_url(True)
        data = self.client.get(public_url)
        self.assertIn('BEGIN:VCALENDAR', data.content.decode('utf8'))

    def test_unusual_event_export(self):
        """ verify that incomplete and unusual events can be exported """
        # "until_time" is the only optional event attribute
        self.create_group_event(title='Missing End Time', missing_keys={'until_time'})
        # "all_day" is not enabled by default
        self.create_group_event(title='All Day Event', all_day=True)
        calendar_url = self.get_calendar_export_url(False)
        data = self.client.get(calendar_url).content.decode('utf8')
        self.assertIn('BEGIN:VCALENDAR', data)
        self.assertIn('Missing End Time', data)
        self.assertIn('All Day Event', data)


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


class TestUrls(core.tests.Test):
    def test_events_404(self):
        r = self.client.get(django.urls.reverse('day-events', args=[1970, 1, 1]))
        self.assertEqual(r.status_code, 404)
        r = self.client.get(self.get_url('create-group-event', 'non-existent'))
        self.assertEqual(r.status_code, 404)
        r = self.client.get(django.urls.reverse(
            'gestalt-events-feed', args=['non-existent', 'public']))
        self.assertEqual(r.status_code, 404)
        r = self.client.get(self.get_url('group-events-export', 'non-existent'))
        self.assertEqual(r.status_code, 404)
        r = self.client.get(django.urls.reverse(
            'group-events-feed', args=['non-existent', 'public']))
