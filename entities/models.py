from django.db import models


class Gestalt(models.Model):
    pass


class Group(models.Model):
    address = models.TextField(blank=True)
    date_created = models.DateField(auto_now_add=True)
    date_founded = models.DateField(null=True, blank=True)
    logo = models.ImageField(blank=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    url = models.URLField(blank=True)

    def __str__(self):
        return self.name
