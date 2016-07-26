from . import models
from utils import tests


class NoLink:
    def test_content(self):
        response = self.client.get(self.content.get_absolute_url())
        self.assertNotContainsLink(
                response, 'content-subscribe', self.content.pk)
        self.assertNotContainsLink(
                response, 'content-unsubscribe', self.content.pk)


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
