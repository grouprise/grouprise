from django.conf import settings
from django.db import models


class Gestalt(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='gestalt')
    
    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.pk:
            try:
                gestalt = Gestalt.objects.get(user=self.user)
                self.pk = gestalt.pk
            except Gestalt.DoesNotExist:
                pass
        super().save(*args, **kwargs)


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
