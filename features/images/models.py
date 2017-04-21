from django.db import models


class Image(models.Model):
    file = models.ImageField('Datei')
    creator = models.ForeignKey('gestalten.Gestalt', related_name='images')
