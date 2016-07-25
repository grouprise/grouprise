from . import models
from utils import tests


class GroupSubscribedMixin(tests.AuthenticatedMixin, tests.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Subscription.objects.create(
                subscribed_to=cls.group, subscriber=cls.gestalt)


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


class GroupSubscribeAllowedMixin:
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


class GroupSubscribeForbiddenMixin:
    def test_group_subscribe(self):
        self.assertRequest(
                methods=[tests.HTTP_GET, tests.HTTP_POST],
                url='group-subscribe', key=self.group.pk,
                response={tests.HTTP_FORBIDDEN_OR_LOGIN})


class GroupUnsubscribeAllowedMixin:
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


class GroupUnsubscribeForbiddenMixin:
    def test_group_unsubscribe(self):
        self.assertRequest(
                methods=[tests.HTTP_GET, tests.HTTP_POST],
                url='group-unsubscribe', key=self.group.pk,
                response={tests.HTTP_FORBIDDEN_OR_LOGIN})


class Anonymous(
        OnlySubscribeLinkMixin,
        GroupSubscribeForbiddenMixin,
        GroupUnsubscribeForbiddenMixin,
        tests.GroupMixin, tests.Test):
    pass


class Authenticated(
        OnlySubscribeLinkMixin,
        GroupSubscribeAllowedMixin,
        GroupUnsubscribeForbiddenMixin,
        tests.AuthenticatedMixin, tests.GroupMixin, tests.Test):
    pass


class Member(
        NoLinkMixin,
        GroupSubscribeForbiddenMixin,
        GroupUnsubscribeForbiddenMixin,
        tests.MemberMixin, tests.Test):
    pass


class GroupSubscribed(
        OnlyUnsubscribeLinkMixin,
        GroupSubscribeForbiddenMixin,
        GroupUnsubscribeAllowedMixin,
        GroupSubscribedMixin, tests.Test):
    pass


class GroupSubscribedMember(
        OnlyUnsubscribeLinkMixin,
        GroupSubscribeForbiddenMixin,
        GroupUnsubscribeAllowedMixin,
        GroupSubscribedMixin, tests.MemberMixin, tests.Test):
    pass
