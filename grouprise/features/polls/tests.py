import django.core.mail
from django.urls import reverse

import grouprise.core.tests
import grouprise.features.gestalten.tests
import grouprise.features.gestalten.tests.mixins
from grouprise.features.associations import models as associations
from grouprise.features.contributions import models as contributions
from grouprise.features.memberships import test_mixins as memberships


def get_post_data():
    return {
        "title": "Test",
        "text": "Test",
        "vote_type": "simple",
        "poll_type": "simple",
        "form-TOTAL_FORMS": "5",
        "form-INITIAL_FORMS": "0",
        "form-MIN_NUM_FORMS": "1",
        "form-MAX_NUM_FORMS": "1000",
        "form-0-title": "Test",
        "as_gestalt": True,
    }


def get_vote_data(anon=None):
    data = {
        "form-TOTAL_FORMS": "1",
        "form-INITIAL_FORMS": "0",
        "form-MIN_NUM_FORMS": "0",
        "form-MAX_NUM_FORMS": "1000",
    }
    if anon:
        data["anonymous"] = anon
    return data


class PollMixin(grouprise.features.gestalten.tests.mixins.AuthenticatedMixin):
    def get_post_data(self):
        return get_post_data()

    def create_poll(self, **kwargs):
        kwargs.update(self.get_post_data())
        self.client.post(self.get_url("create-poll"), kwargs)
        return associations.Association.objects.get(content__title="Test")

    def get_content_url(self):
        return self.get_url(
            "content", (self.association.entity.slug, self.association.slug)
        )

    def setUp(self):
        super().setUp()
        self.association = self.create_poll()
        django.core.mail.outbox = []


class GroupPollMixin(PollMixin):
    def create_poll(self, **kwargs):
        kwargs.update(self.get_post_data())
        self.client.post(self.get_url("create-group-poll", self.group.slug), kwargs)
        return associations.Association.objects.get(content__title="Test")


class Guest(memberships.MemberMixin, grouprise.core.tests.Test):
    def create_poll(self, **kwargs):
        self.client.force_login(self.gestalt.user)
        kwargs.update(get_post_data())
        self.client.post(self.get_url("create-poll"), kwargs)
        self.client.logout()

    def get_poll_association(self):
        return associations.Association.objects.get(content__title="Test")

    def get_poll_url(self):
        return self.get_poll_association().get_absolute_url()

    def get_vote_url(self):
        association = self.get_poll_association()
        return self.get_url("vote", [association.entity.slug, association.slug])

    def create_group_poll(self, **kwargs):
        self.client.force_login(self.gestalt.user)
        kwargs.update(get_post_data())
        self.client.post(self.get_url("create-group-poll", self.group.slug), kwargs)
        self.client.logout()

    def get_group_poll_url(self):
        return associations.Association.objects.get(
            content__title="Test"
        ).get_absolute_url()

    def test_guest_poll_link(self):
        self.assertNotContainsLink(self.client.get("/"), self.get_url("create-poll"))
        self.assertNotContainsLink(
            self.client.get(self.gestalt.get_absolute_url()),
            self.get_url("create-poll"),
        )
        self.assertNotContainsLink(
            self.client.get(self.group.get_absolute_url()), self.get_url("create-poll")
        )

    def test_guest_create_poll(self):
        self.assertLogin(url_name="create-poll")
        self.assertLogin(url_name="create-poll", method="post")

    def test_guest_create_group_poll(self):
        self.assertLogin(url_name="create-group-poll", url_args=[self.group.slug])
        self.assertLogin(
            url_name="create-group-poll", url_args=[self.group.slug], method="post"
        )

    def test_guest_public_poll(self):
        self.create_poll(public=True)
        self.assertContainsLink(self.client.get("/"), self.get_poll_url())
        self.assertContainsLink(
            self.client.get(self.gestalt.get_absolute_url()), self.get_poll_url()
        )
        self.assertOk(url=self.get_poll_url())

    def test_guest_internal_poll(self):
        self.create_poll(public=False)
        self.assertNotContainsLink(self.client.get("/"), self.get_poll_url())
        self.assertNotContainsLink(
            self.client.get(self.gestalt.get_absolute_url()), self.get_poll_url()
        )
        self.assertLogin(url=self.get_poll_url())

    def test_guest_public_group_poll(self):
        self.create_group_poll(public=True)
        self.assertContainsLink(obj=self.group, link_url=self.get_group_poll_url())
        self.assertOk(url=self.get_group_poll_url())
        self.assertLogin(url=self.get_group_poll_url(), method="post")

    def test_guest_internal_group_poll(self):
        self.create_group_poll(public=False)
        self.assertNotContainsLink(obj=self.group, link_url=self.get_group_poll_url())
        self.assertLogin(url=self.get_group_poll_url())
        self.assertLogin(url=self.get_group_poll_url(), method="post")

    def test_guest_public_poll_vote(self):
        self.create_poll(public=True)
        self.assertRedirect(
            self.get_vote_url(),
            method="post",
            data=get_vote_data(anon="a"),
            other=self.get_poll_url(),
        )

    def test_guest_internal_poll_vote(self):
        self.create_poll(public=False)
        self.assertLogin(self.get_vote_url(), method="post")


class Gestalt(memberships.AuthenticatedMemberMixin, grouprise.core.tests.Test):
    def create_poll(self, **kwargs):
        kwargs.update(get_post_data())
        return self.client.post(self.get_url("create-poll"), kwargs)

    def create_group_poll(self, **kwargs):
        kwargs.update(get_post_data())
        return self.client.post(
            self.get_url("create-group-poll", self.group.slug), kwargs
        )

    def get_poll_association(self):
        return associations.Association.objects.get(content__title="Test")

    def get_poll_url(self):
        return self.get_poll_association().get_absolute_url()

    def get_vote_url(self):
        association = self.get_poll_association()
        return self.get_url("vote", [association.entity.slug, association.slug])

    def get_group_poll_url(self):
        return associations.Association.objects.get(
            content__title="Test"
        ).get_absolute_url()

    def test_gestalt_poll_link(self):
        self.assertContainsLink(self.client.get("/"), self.get_url("create-poll"))
        self.assertContainsLink(
            self.client.get(self.gestalt.get_absolute_url()),
            self.get_url("create-poll"),
        )
        self.assertContainsLink(
            self.client.get(self.group.get_absolute_url()),
            self.get_url("create-group-poll", self.group.slug),
        )

    def test_gestalt_create_poll(self):
        self.assertEqual(self.client.get(self.get_url("create-poll")).status_code, 200)
        response = self.create_poll()
        self.assertRedirects(response, self.get_poll_url())
        self.assertExists(associations.Association, content__title="Test")

    def test_gestalt_create_group_poll(self):
        self.assertEqual(
            self.client.get(
                self.get_url("create-group-poll", self.group.slug)
            ).status_code,
            200,
        )
        response = self.create_group_poll()
        self.assertRedirects(response, self.get_group_poll_url())
        self.assertExists(associations.Association, content__title="Test")

    def test_gestalt_public_poll(self):
        self.create_poll(public=True)
        self.assertContainsLink(self.client.get("/"), self.get_poll_url())
        self.assertContainsLink(
            self.client.get(self.gestalt.get_absolute_url()), self.get_poll_url()
        )
        self.assertOk(url=self.get_poll_url())

    def test_gestalt_internal_poll(self):
        self.create_poll(public=False)
        self.assertContainsLink(self.client.get("/"), self.get_poll_url())
        self.assertContainsLink(
            self.client.get(self.gestalt.get_absolute_url()), self.get_poll_url()
        )
        self.assertOk(url=self.get_poll_url())

    def test_gestalt_public_group_poll(self):
        self.create_group_poll(public=True)
        self.assertContainsLink(obj=self.group, link_url=self.get_group_poll_url())
        self.assertOk(url=self.get_group_poll_url())

    def test_gestalt_internal_group_poll(self):
        self.create_group_poll(public=False)
        self.assertContainsLink(obj=self.group, link_url=self.get_group_poll_url())
        self.assertOk(url=self.get_group_poll_url())

    def test_gestalt_comment_poll(self):
        self.create_poll()
        self.assertRedirect(
            url=self.get_poll_url(), method="post", data={"text": "Comment"}
        )
        self.assertExists(contributions.Contribution, text__text="Comment")

    def test_gestalt_public_poll_vote(self):
        self.create_poll(public=True)
        self.assertRedirect(
            self.get_vote_url(),
            method="post",
            data=get_vote_data(),
            other=self.get_poll_url(),
        )

    def test_gestalt_internal_poll_vote(self):
        self.create_group_poll(public=False)
        self.assertRedirect(
            self.get_vote_url(),
            method="post",
            data=get_vote_data(),
            other=self.get_poll_url(),
        )


class TwoGestalten(
    memberships.OtherMemberMixin,
    memberships.AuthenticatedMemberMixin,
    grouprise.core.tests.Test,
):
    def create_poll(self, **kwargs):
        kwargs.update(get_post_data())
        self.client.post(self.get_url("create-group-poll", self.group.slug), kwargs)
        self.association = associations.Association.objects.get(content__title="Test")

    def get_content_url(self):
        return self.get_url(
            "content", (self.association.entity.slug, self.association.slug)
        )

    def test_poll_notified(self):
        self.create_poll()
        self.assertNotificationsSent(2)
        self.assertNotificationRecipient(self.gestalt)
        self.assertNotificationRecipient(self.other_gestalt)
        self.assertNotificationContains(
            reverse("content-permalink", args=[self.association.pk])
        )
        self.assertNotificationContains("Test")


class GestaltAndPoll(PollMixin, grouprise.core.tests.Test):
    def create_comment(self, **kwargs):
        kwargs.update({"text": "Comment"})
        return self.client.post(self.get_content_url(), kwargs)

    def test_poll_comment_self_notified(self):
        self.create_comment()
        self.assertNotificationsSent(1)
        self.assertNotificationRecipient(self.gestalt)
        self.assertNotificationContains(
            reverse("content-permalink", args=[self.association.pk])
        )
        self.assertNotificationContains("Comment")


class TwoGestaltenAndGroupPoll(
    GroupPollMixin,
    memberships.OtherMemberMixin,
    memberships.AuthenticatedMemberMixin,
    grouprise.core.tests.Test,
):
    def create_comment(self, **kwargs):
        kwargs.update({"text": "Comment"})
        return self.client.post(self.get_content_url(), kwargs)

    def test_poll_comment_both_notified(self):
        self.create_comment()
        self.assertNotificationsSent(2)
        self.assertNotificationRecipient(self.other_gestalt)
