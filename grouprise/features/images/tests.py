import os.path
import shutil

import django.conf

import grouprise.features.gestalten.tests
import grouprise.features.gestalten.tests.mixins
from . import models


class ImageMixin(grouprise.features.gestalten.tests.mixins.GestaltMixin):
    def setUp(self):
        super().setUp()
        test_image = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "tests", "test.png"
        )
        shutil.copy(test_image, django.conf.settings.MEDIA_ROOT)
        self.image = models.Image.objects.create(
            creator=self.gestalt, file="./test.png"
        )
