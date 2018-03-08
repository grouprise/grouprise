from django.contrib import auth
from django.urls import reverse
from django.test import TestCase


class GestaltMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.gestalt = auth.get_user_model().objects.create(
                email='test@example.org', username='test').gestalt
        cls.gestalt.public = True
        cls.gestalt.save()
        cls.gestalt.user.emailaddress_set.create(email='test@example.org')


class OtherGestaltMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.other_gestalt = auth.get_user_model().objects.create(
                email='test2@example.org', username='test2').gestalt


class AuthenticatedMixin(GestaltMixin):
    def setUp(self):
        super().setUp()
        self.client.force_login(
                self.gestalt.user, 'django.contrib.auth.backends.ModelBackend')


class OtherAuthenticatedMixin(OtherGestaltMixin):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.other_gestalt.user,
                                'django.contrib.auth.backends.ModelBackend')


class Gestalt(GestaltMixin, TestCase):
    def test_private_gestalt_page(self):
        self.gestalt.public = False
        self.gestalt.save()
        gestalt_url = reverse('entity', args=(self.gestalt.user.username,))
        r = self.client.get(gestalt_url)
        self.assertRedirects(r, '{}?next={}'.format(reverse('account_login'), gestalt_url))

    def test_public_gestalt_page(self):
        self.gestalt.public = True
        self.gestalt.save()
        gestalt_url = reverse('entity', args=(self.gestalt.user.username,))
        r = self.client.get(gestalt_url)
        self.assertEqual(r.status_code, 200)


class Settings(TestCase):
    def test_settings(self):
        # general settings not accessible
        r = self.client.get('/')
        self.assertNotContains(r, 'href="{}"'.format(reverse('settings')))
        r = self.client.get(reverse('settings'))
        self.assertEqual(r.status_code, 302)


class AuthenticatedSettings(AuthenticatedMixin, TestCase):
    def test_authenticated_settings(self):
        # general settings accessible
        r = self.client.get('/')
        self.assertContains(r, 'href="{}"'.format(reverse('settings')))
        r = self.client.get(reverse('settings'))
        self.assertEqual(r.status_code, 200)

        # save form with changed values
        r = self.client.post(reverse('settings'), {'slug': 'changed-username'})
        self.gestalt.user.refresh_from_db()
        self.assertRedirects(r, self.gestalt.get_profile_url())
        self.assertEqual(self.gestalt.user.username, 'changed-username')

    def test_other_settings(self):
        image_settings_url = reverse('image-settings')
        email_settings_url = reverse('email-settings')
        password_settings_url = reverse('password-settings')

        r = self.client.get(reverse('settings'))
        self.assertContains(r, 'href="{}'.format(image_settings_url))
        self.assertContains(r, 'href="{}'.format(email_settings_url))
        self.assertContains(r, 'href="{}'.format(password_settings_url))
        r = self.client.get(image_settings_url)
        self.assertEqual(r.status_code, 200)
        r = self.client.get(email_settings_url)
        self.assertEqual(r.status_code, 200)
        r = self.client.get(password_settings_url)
        self.assertEqual(r.status_code, 302)
