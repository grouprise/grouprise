from django.contrib import auth
from django.core.urlresolvers import reverse
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
        self.assertRedirects(r, '{}?next={}'.format(reverse('login'), gestalt_url))

    def test_public_gestalt_page(self):
        self.gestalt.public = True
        self.gestalt.save()
        gestalt_url = reverse('entity', args=(self.gestalt.user.username,))
        r = self.client.get(gestalt_url)
        self.assertEqual(r.status_code, 200)
