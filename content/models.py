import autoslug
from django.core import urlresolvers
from django.db import models
from django.utils import text, timezone
from entities import models as entities_models


class Image(models.Model):
    content = models.ForeignKey('Content')
    image = models.ImageField()


class Base(models.Model):
    author = models.ForeignKey('entities.Gestalt')
    date_created = models.DateTimeField(default=timezone.now)
    text = models.TextField('Text', blank=True)

    class Meta:
        abstract = True
        ordering = ('-date_created',)


class Comment(Base):
    content = models.ForeignKey('Content')


class Content(Base):
    subclass_names = ['Article', 'Event', 'Gallery']

    slug = autoslug.AutoSlugField(populate_from='title', unique=True)
    title = models.CharField('Titel', max_length=255)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return urlresolvers.reverse('content', args=[self.author.user.username, self.slug])

    def get_display_type_name(self):
        return self.get_subclass_instance().display_type_name

    def get_subclass_instance(self):
        import sys
        for subclass_name in self.subclass_names:
            try:
                return getattr(self, subclass_name.lower())
            except getattr(sys.modules[__name__], subclass_name).DoesNotExist:
                pass

    def groups(self):
        return entities_models.Group.objects.filter(groupcontent__content=self)


class Article(Content):
    display_type_name = 'Artikel'
    

class Event(Content):
    display_type_name = 'Termin'

    place = models.CharField(max_length=255)
    time = models.DateTimeField()


class Gallery(Content):
    display_type_name = 'Galerie'
