from django.contrib import auth


class GestaltMixin:
    @classmethod
    def create_gestalt(cls, name="test"):
        email = f"{name}@example.org"
        gestalt = (
            auth.get_user_model().objects.create(email=email, username=name).gestalt
        )
        gestalt.public = True
        gestalt.save()
        gestalt.user.emailaddress_set.create(email=email)
        return gestalt

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # create an initial gestalt which is used as special user
        # (imports, unknown etc.)
        cls.unknown_gestalt = cls.create_gestalt(name="inital")
        cls.gestalt = cls.create_gestalt()


class OtherGestaltMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.other_gestalt = (
            auth.get_user_model()
            .objects.create(email="test2@example.org", username="test2")
            .gestalt
        )


class AuthenticatedMixin(GestaltMixin):
    def setUp(self):
        super().setUp()
        self.client.force_login(
            self.gestalt.user, "django.contrib.auth.backends.ModelBackend"
        )


class OtherAuthenticatedMixin(OtherGestaltMixin):
    def setUp(self):
        super().setUp()
        self.client.force_login(
            self.other_gestalt.user, "django.contrib.auth.backends.ModelBackend"
        )
