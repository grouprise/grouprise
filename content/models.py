from django.db import models


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
    views = models.PositiveIntegerField()

    def __str__(self):
        return self.title


class Article(Content):
    pass
