from django.db import models


class GalleryImage(models.Model):
    gallery = models.ForeignKey('content2.Content', related_name='gallery_images')
    image = models.ForeignKey('images.Image', related_name='+')
