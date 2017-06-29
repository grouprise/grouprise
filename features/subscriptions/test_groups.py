from core import tests
from core.tests import get_url as u
from . import models


class NoLink:
    def test_group(self):
        response = self.client.get(self.group.get_absolute_url())
        self.assertNotContainsLink(response, self.get_url('group-subscribe', self.group.pk))
        self.assertNotContainsLink(
                response, self.get_url('group-unsubscribe', self.group.pk))


class OnlySubscribeLink:
    def test_group(self):
        response = self.client.get(self.group.get_absolute_url())
        self.assertContainsLink(response, self.get_url('group-subscribe', self.group.pk))
        self.assertNotContainsLink(
                response, self.get_url('group-unsubscribe', self.group.pk))


class OnlyUnsubscribeLink:
    def test_group(self):
        response = self.client.get(self.group.get_absolute_url())
        self.assertNotContainsLink(response, self.get_url('group-subscribe', self.group.pk))
        self.assertContainsLink(response, self.get_url('group-unsubscribe', self.group.pk))


class SubscribeAllowed:
    def test_group_subscribe(self):
        self.assertRequest(
                methods=[tests.HTTP_GET],
                url='group-subscribe', key=self.group.pk,
                response={tests.HTTP_OK})
        response = self.client.post(self.get_url('group-subscribe', key=self.group.pk))
        self.assertRedirects(response, self.group.get_absolute_url())
        self.assertExists(
                models.Subscription,
                subscribed_to=self.group, subscriber=self.gestalt)


class SubscribeAllowedWithEmail:
    def test_group_subscribe(self):
        self.assertRequest(
                methods=[tests.HTTP_GET],
                url='group-subscribe', key=self.group.pk,
                response={tests.HTTP_OK})
        response = self.client.post(
                self.get_url('group-subscribe', self.group.pk),
                {'subscriber_email': self.gestalt.user.email})
        self.assertRedirects(response, self.group.get_absolute_url())
        self.assertExists(
                models.Subscription,
                subscribed_to=self.group, subscriber=self.gestalt)


class SubscribeForbidden:
    def test_group_subscribe(self):
        self.assertRequest(
                methods=[tests.HTTP_GET, tests.HTTP_POST],
                url='group-subscribe', key=self.group.pk,
                response={tests.HTTP_FORBIDDEN_OR_LOGIN})


class SubscribeRedirectToGroupPage:
    def test_group_subscribe(self):
        r = self.client.get(u('group-subscribe', self.group.pk))
        self.assertRedirects(r, self.group.get_absolute_url())
        r = self.client.post(u('group-subscribe', self.group.pk))
        self.assertRedirects(r, self.group.get_absolute_url())


class UnsubscribeAllowed:
    def test_group_unsubscribe(self):
        self.assertRequest(
                methods=[tests.HTTP_GET],
                url='group-unsubscribe', key=self.group.pk,
                response={tests.HTTP_OK})
        response = self.client.post(self.get_url('group-unsubscribe', key=self.group.pk))
        self.assertRedirects(response, self.group.get_absolute_url())
        self.assertNotExists(
                models.Subscription,
                subscribed_to=self.group, subscriber=self.gestalt)


class UnsubscribeForbidden:
    def test_group_unsubscribe(self):
        self.assertRequest(
                methods=[tests.HTTP_GET, tests.HTTP_POST],
                url='group-unsubscribe', key=self.group.pk,
                response={tests.HTTP_FORBIDDEN_OR_LOGIN})
