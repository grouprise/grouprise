from django.db import models


class GalleryImage(models.Model):
    gallery = models.ForeignKey('content2.Content', related_name='+')
    image = models.ForeignKey('images.Image', related_name='+')
