from django.db import models


class Image(models.Model):
    content = models.ForeignKey('Content')
    image = models.ImageField()


class Base(models.Model):
    author = models.ForeignKey('entities.Gestalt')
    date_created = models.DateField(auto_now_add=True)
    text = models.TextField(blank=True)

    class Meta:
        abstract = True


class Comment(Base):
    content = models.ForeignKey('Content')


class Content(Base):
    title = models.CharField(max_length=255)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def get_display_type_name(self):
        return self.get_subclass_instance().display_type_name

    def get_subclass_instance(self):
        subclass_instance_list = [self.article]
        objects = [o for o in subclass_instance_list if o]
        return objects[0] if objects else None


class Article(Content):
    display_type_name = 'Artikel'
