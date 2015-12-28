import autoslug

from django.conf import settings
from django.db import models

from . import querysets


class Gestalt(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    
    def __str__(self):
        name = ' '.join(filter(None, [self.user.first_name, self.user.last_name]))
        return name if name else self.user.username


class Group(models.Model):
    address = models.TextField(blank=True)
    avatar = models.ImageField(blank=True)
    date_created = models.DateField(auto_now_add=True)
    date_founded = models.DateField(null=True, blank=True)
    logo = models.ImageField(blank=True)
    name = models.CharField(max_length=255)
    slug = autoslug.AutoSlugField(populate_from='name', unique=True)
    url = models.URLField(blank=True)

    def __str__(self):
        return self.name


class GroupContent(models.Model):
    content = models.OneToOneField('content.Content')
    group = models.ForeignKey('Group')
    pinned = models.BooleanField()

    objects = models.Manager.from_queryset(querysets.GroupContentQuerySet)()

    def __str__(self):
        return self.content.title


class Membership(models.Model):
    date_joined = models.DateField(auto_now_add=True)
    gestalt = models.ForeignKey('Gestalt')
    group = models.ForeignKey('Group')

    class Meta:
        unique_together = ('gestalt', 'group')
