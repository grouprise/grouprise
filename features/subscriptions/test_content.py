from . import models
from core import tests


class NoLink:
    def test_content(self):
        response = self.client.get(self.content.get_absolute_url())
        self.assertNotContainsLink(
                response, 'content-subscribe', self.content.pk)
        self.assertNotContainsLink(
                response, 'content-unsubscribe', self.content.pk)
        if hasattr(self, 'group'):
            self.assertNotContainsLink(response, 'external-content-unsubscribe', self.group.pk)


class OnlySubscribeLink:
    def test_content(self):
        response = self.client.get(self.content.get_absolute_url())
        self.assertContainsLink(response, 'content-subscribe', self.content.pk)
        self.assertNotContainsLink(
                response, 'content-unsubscribe', self.content.pk)


class OnlyUnsubscribeLink:
    def test_content(self):
        response = self.client.get(self.content.get_absolute_url())
        self.assertNotContainsLink(
                response, 'content-subscribe', self.content.pk)
        self.assertContainsLink(
                response, 'content-unsubscribe', self.content.pk)


class ExternalUnsubscribeLink:
    def test_content(self):
        response = self.client.get(self.content.get_absolute_url())
        self.assertContainsLink(
                response, 'external-content-unsubscribe', self.group.pk)


class SubscribeAllowed:
    def test_content_subscribe(self):
        self.assertRequest(
                methods=[tests.HTTP_GET],
                url='content-subscribe', key=self.content.pk,
                response={tests.HTTP_OK})
        self.assertRequest(
                methods=[tests.HTTP_POST],
                url='content-subscribe', key=self.content.pk,
                response={
                    tests.HTTP_REDIRECTS: self.content.get_absolute_url()})
        self.assertExists(
                models.Subscription,
                subscribed_to=self.content, subscriber=self.gestalt)


class SubscribeAllowedWithEmail:
    def test_content_subscribe(self):
        self.assertRequest(
                methods=[tests.HTTP_GET],
                url='content-subscribe', key=self.content.pk,
                response={tests.HTTP_OK})
        response = self.client.post(
                self.get_url('content-subscribe', self.content.pk),
                {'subscriber_email': self.gestalt.user.email})
        self.assertRedirects(response, self.content.get_absolute_url())
        self.assertExists(
                models.Subscription,
                subscribed_to=self.content, subscriber=self.gestalt)


class SubscribeForbidden:
    def test_content_subscribe(self):
        self.assertRequest(
                methods=[tests.HTTP_GET, tests.HTTP_POST],
                url='content-subscribe', key=self.content.pk,
                response={tests.HTTP_FORBIDDEN_OR_LOGIN})


class UnsubscribeAllowed:
    def test_content_unsubscribe(self):
        self.assertRequest(
                methods=[tests.HTTP_GET],
                url='content-unsubscribe', key=self.content.pk,
                response={tests.HTTP_OK})
        self.assertRequest(
                methods=[tests.HTTP_POST],
                url='content-unsubscribe', key=self.content.pk,
                response={
                    tests.HTTP_REDIRECTS: self.content.get_absolute_url()})
        self.assertNotExists(
                models.Subscription,
                subscribed_to=self.content, subscriber=self.gestalt)


class UnsubscribeForbidden:
    def test_content_unsubscribe(self):
        self.assertRequest(
                methods=[tests.HTTP_GET, tests.HTTP_POST],
                url='content-unsubscribe', key=self.content.pk,
                response={tests.HTTP_FORBIDDEN_OR_LOGIN})


class ExternalUnsubscribeAllowed:
    def test_external_unsubscribe(self):
        self.assertRequest(
                methods=[tests.HTTP_GET],
                url='external-content-unsubscribe', key=self.group.pk,
                response={tests.HTTP_OK})
        self.assertRequest(
                methods=[tests.HTTP_POST],
                url='external-content-unsubscribe', key=self.group.pk,
                response={
                    tests.HTTP_REDIRECTS: self.group.get_absolute_url()})
        self.assertExists(
                models.Unsubscription,
                subscribed_to=self.group, subscriber=self.gestalt)


class ExternalUnsubscribeForbidden:
    def test_external_unsubscribe(self):
        self.assertRequest(
                methods=[tests.HTTP_GET, tests.HTTP_POST],
                url='external-content-unsubscribe', key=self.group.pk,
                response={tests.HTTP_FORBIDDEN_OR_LOGIN})
