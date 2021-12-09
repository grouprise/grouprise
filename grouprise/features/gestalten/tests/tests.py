from django.contrib import auth
from django.test import TestCase
from django.urls import reverse

from grouprise.features.articles.tests import ArticleMixin
from grouprise.features.contributions.tests import ContributionMixin
from grouprise.features.gestalten import models
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.gestalten.tests.mixins import AuthenticatedMixin, GestaltMixin


class GestaltTestCase(GestaltMixin, TestCase):
    def test_private_gestalt_page(self):
        self.gestalt.public = False
        self.gestalt.save()
        gestalt_url = reverse("entity", args=(self.gestalt.user.username,))
        r = self.client.get(gestalt_url)
        self.assertRedirects(
            r, "{}?next={}".format(reverse("account_login"), gestalt_url)
        )

    def test_public_gestalt_page(self):
        self.gestalt.public = True
        self.gestalt.save()
        gestalt_url = reverse("entity", args=(self.gestalt.user.username,))
        r = self.client.get(gestalt_url)
        self.assertEqual(r.status_code, 200)


class GestaltWithContributionTestCase(ContributionMixin, GestaltMixin, TestCase):
    def test_delete_gestalt_with_deleted_contribution(self):
        """
        Deleting a gestalt who authors a deleted contribution should succeed.

        Regression test for #753.
        """
        self.mark_contribution_deleted()
        num_gestalten = Gestalt.objects.count()
        self.gestalt.delete()
        self.contribution.refresh_from_db()
        self.assertEqual(Gestalt.objects.count(), num_gestalten - 1)
        self.assertEqual(self.contribution.author, self.unknown_gestalt)


class GestaltWithArticleTestCase(ArticleMixin, GestaltMixin, TestCase):
    def test_delete_gestalt_with_deleted_association(self):
        """Deleting a gestalt who authors a deleted article should succeed."""
        self.mark_article_deleted()
        num_gestalten = Gestalt.objects.count()
        self.gestalt.delete()
        self.association.refresh_from_db()
        self.assertEqual(Gestalt.objects.count(), num_gestalten - 1)
        self.assertEqual(self.association.entity, self.unknown_gestalt)


class Settings(TestCase):
    def test_settings(self):
        # general settings not accessible
        r = self.client.get("/")
        self.assertNotContains(r, 'href="{}"'.format(reverse("settings")))
        r = self.client.get(reverse("settings"))
        self.assertEqual(r.status_code, 302)


class AuthenticatedSettings(AuthenticatedMixin, TestCase):
    def setUp(self):
        auth.get_user_model().objects.create(
            email="unknown@example.org", username="unknown"
        )
        super().setUp()

    def test_authenticated_settings(self):
        # general settings accessible
        r = self.client.get("/")
        self.assertContains(r, 'href="{}"'.format(reverse("settings")))
        r = self.client.get(reverse("settings"))
        self.assertEqual(r.status_code, 200)

        # save form with changed values
        r = self.client.post(reverse("settings"), {"slug": "changed-username"})
        self.gestalt.user.refresh_from_db()
        self.assertRedirects(r, self.gestalt.get_profile_url())
        self.assertEqual(self.gestalt.user.username, "changed-username")

    def test_other_settings(self):
        image_settings_url = reverse("image-settings")
        email_settings_url = reverse("email-settings")
        password_settings_url = reverse("account_change_password")

        r = self.client.get(reverse("settings"))
        self.assertContains(r, 'href="{}'.format(image_settings_url))
        self.assertContains(r, 'href="{}'.format(email_settings_url))
        self.assertContains(r, 'href="{}'.format(password_settings_url))
        r = self.client.get(image_settings_url)
        self.assertEqual(r.status_code, 200)
        r = self.client.get(email_settings_url)
        self.assertEqual(r.status_code, 200)
        r = self.client.get(password_settings_url)
        self.assertEqual(r.status_code, 200)

    def test_delete(self):
        delete_url = reverse("delete-gestalt")

        r = self.client.get(reverse("settings"))
        self.assertContains(r, 'href="{}'.format(delete_url))
        r = self.client.get(delete_url)
        self.assertEqual(r.status_code, 200)
        r = self.client.post(delete_url)
        self.assertRedirects(r, "/")
        self.assertFalse(models.Gestalt.objects.filter(pk=self.gestalt.pk).exists())
