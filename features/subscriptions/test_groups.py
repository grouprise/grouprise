from . import models
from utils import tests


class NoLinkMixin:
    def test_group(self):
        response = self.request(
                tests.HTTP_GET, url='group', key=self.group.slug)
        self.assertNotContainsLink(response, 'group-subscribe', self.group.pk)
        self.assertNotContainsLink(
                response, 'group-unsubscribe', self.group.pk)


class OnlySubscribeLinkMixin:
    def test_group(self):
        response = self.request(
                tests.HTTP_GET, url='group', key=self.group.slug)
        self.assertContainsLink(response, 'group-subscribe', self.group.pk)
        self.assertNotContainsLink(
                response, 'group-unsubscribe', self.group.pk)


class OnlyUnsubscribeLinkMixin:
    def test_group(self):
        response = self.request(
                tests.HTTP_GET, url='group', key=self.group.slug)
        self.assertNotContainsLink(response, 'group-subscribe', self.group.pk)
        self.assertContainsLink(response, 'group-unsubscribe', self.group.pk)


class SubscribeAllowedMixin:
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


class SubscribeForbiddenMixin:
    def test_group_subscribe(self):
        self.assertRequest(
                methods=[tests.HTTP_GET, tests.HTTP_POST],
                url='group-subscribe', key=self.group.pk,
                response={tests.HTTP_FORBIDDEN_OR_LOGIN})


class UnsubscribeAllowedMixin:
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


class UnsubscribeForbiddenMixin:
    def test_group_unsubscribe(self):
        self.assertRequest(
                methods=[tests.HTTP_GET, tests.HTTP_POST],
                url='group-unsubscribe', key=self.group.pk,
                response={tests.HTTP_FORBIDDEN_OR_LOGIN})
