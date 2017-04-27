import os.path
import shutil

import django.conf

from features.gestalten import tests as gestalten
from . import models


class ImageMixin(gestalten.GestaltMixin):
    def setUp(self):
        super().setUp()
        test_image = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'tests', 'test.png')
        shutil.copy(test_image, django.conf.settings.MEDIA_ROOT)
        self.image = models.Image.objects.create(creator=self.gestalt, file='./test.png')
