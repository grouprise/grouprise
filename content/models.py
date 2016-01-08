import autoslug

from django.db import models
from django.utils import text, timezone


class Image(models.Model):
    content = models.ForeignKey('Content')
    image = models.ImageField()


class Base(models.Model):
    author = models.ForeignKey('entities.Gestalt')
    date_created = models.DateTimeField(default=timezone.now)
    text = models.TextField(blank=True)

    class Meta:
        abstract = True


class Comment(Base):
    content = models.ForeignKey('Content')


class Content(Base):
    subclass_names = ['Article', 'Event', 'Gallery']

    slug = autoslug.AutoSlugField(populate_from='title', unique=True)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    def get_display_type_name(self):
        return self.get_subclass_instance().display_type_name

    def get_subclass_instance(self):
        import sys
        for subclass_name in self.subclass_names:
            try:
                return getattr(self, subclass_name.lower())
            except getattr(sys.modules[__name__], subclass_name).DoesNotExist:
                pass


class Article(Content):
    display_type_name = 'Artikel'
    

class Event(Content):
    display_type_name = 'Termin'

    place = models.CharField(max_length=255)
    time = models.DateTimeField()


class Gallery(Content):
    display_type_name = 'Galerie'
