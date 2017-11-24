from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit, SmartResize, Transpose


class Image(models.Model):
    file = models.ImageField('Datei')
    creator = models.ForeignKey('gestalten.Gestalt', related_name='images')

    preview_api = ImageSpecField(
            source='file', processors=[Transpose(), SmartResize(250, 250)], format='PNG')
    preview_content = ImageSpecField(
            source='file', processors=[Transpose(), SmartResize(200, 200)], format='PNG')
    preview_gallery = ImageSpecField(
            source='file', processors=[Transpose(), ResizeToFit(250)], format='PNG')
    preview_group = ImageSpecField(
            source='file', processors=[Transpose(), SmartResize(366, 120)], format='PNG')
    intro = ImageSpecField(
            source='file', processors=[Transpose(), ResizeToFit(554)], format='JPEG')

    def __str__(self):
        return '{} ({})'.format(self.file, self.creator)[2:]
