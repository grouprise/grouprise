from django.db import models


class GalleryImage(models.Model):
    class Meta:
        unique_together = ('gallery', 'image')

    gallery = models.ForeignKey('content2.Content', related_name='gallery_images')
    image = models.ForeignKey('images.Image', related_name='+')
