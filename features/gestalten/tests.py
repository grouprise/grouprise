from django.contrib import auth

import core.tests


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


class TestUrls(core.tests.Test):
    def test_groups_404(self):
        r = self.client.get(self.get_url('gestalt-update', 0))
        self.assertEqual(r.status_code, 404)
        r = self.client.get(self.get_url('gestalt-avatar-update', 0))
        self.assertEqual(r.status_code, 404)
        r = self.client.get(self.get_url('gestalt-background-update', 0))
        self.assertEqual(r.status_code, 404)
