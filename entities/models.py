from django.conf import settings
from django.db import models


class Gestalt(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='gestalt')
    
    def __str__(self):
        return self.user.username


class Group(models.Model):
    address = models.TextField(blank=True)
    avatar = models.ImageField(blank=True)
    date_created = models.DateField(auto_now_add=True)
    date_founded = models.DateField(null=True, blank=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    url = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    date_joined = models.DateField(auto_now_add=True)
    gestalt = models.ForeignKey('Gestalt')
    group = models.ForeignKey('Group')
