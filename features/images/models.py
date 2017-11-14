from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import SmartResize, Transpose


class Image(models.Model):
    file = models.ImageField('Datei')
    creator = models.ForeignKey('gestalten.Gestalt', related_name='images')

    preview = ImageSpecField(source='file', processors=[Transpose(), SmartResize(200, 200)])

    def __str__(self):
        return '{} ({})'.format(self.file, self.creator)[2:]
