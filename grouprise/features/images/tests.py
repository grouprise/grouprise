import os.path
import shutil

import django.conf

import grouprise.features.gestalten.tests
import grouprise.features.gestalten.tests.mixins

from . import models


class ImageMixin(grouprise.features.gestalten.tests.mixins.GestaltMixin):

    IMAGE_BASENAME = "test.png"

    def setUp(self):
        super().setUp()
        test_image = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "tests", self.IMAGE_BASENAME
        )
        shutil.copy(test_image, django.conf.settings.MEDIA_ROOT)
        # the filename refers to the file below MEDIA_ROOT
        self.image = models.Image.objects.create(
            creator=self.gestalt, file=self.IMAGE_BASENAME
        )
