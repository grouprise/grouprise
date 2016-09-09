from . import models
from core import tests


class NoLink:
    def test_group(self):
        response = self.request(
                tests.HTTP_GET, url='group', key=self.group.slug)
        self.assertNotContainsLink(response, 'group-subscribe', self.group.pk)
        self.assertNotContainsLink(
                response, 'group-unsubscribe', self.group.pk)


class OnlySubscribeLink:
    def test_group(self):
        response = self.request(
                tests.HTTP_GET, url='group', key=self.group.slug)
        self.assertContainsLink(response, 'group-subscribe', self.group.pk)
        self.assertNotContainsLink(
                response, 'group-unsubscribe', self.group.pk)


class OnlyUnsubscribeLink:
    def test_group(self):
        response = self.request(
                tests.HTTP_GET, url='group', key=self.group.slug)
        self.assertNotContainsLink(response, 'group-subscribe', self.group.pk)
        self.assertContainsLink(response, 'group-unsubscribe', self.group.pk)


class SubscribeAllowed:
    def test_group_subscribe(self):
        self.assertRequest(
                methods=[tests.HTTP_GET],
                url='group-subscribe', key=self.group.pk,
                response={tests.HTTP_OK})
        self.assertRequest(
                methods=[tests.HTTP_POST],
                url='group-subscribe', key=self.group.pk,
                response={tests.HTTP_REDIRECTS: ('group', self.group.slug)})
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


class UnsubscribeAllowed:
    def test_group_unsubscribe(self):
        self.assertRequest(
                methods=[tests.HTTP_GET],
                url='group-unsubscribe', key=self.group.pk,
                response={tests.HTTP_OK})
        self.assertRequest(
                methods=[tests.HTTP_POST],
                url='group-unsubscribe', key=self.group.pk,
                response={tests.HTTP_REDIRECTS: ('group', self.group.slug)})
        self.assertNotExists(
                models.Subscription,
                subscribed_to=self.group, subscriber=self.gestalt)


class UnsubscribeForbidden:
    def test_group_unsubscribe(self):
        self.assertRequest(
                methods=[tests.HTTP_GET, tests.HTTP_POST],
                url='group-unsubscribe', key=self.group.pk,
                response={tests.HTTP_FORBIDDEN_OR_LOGIN})
