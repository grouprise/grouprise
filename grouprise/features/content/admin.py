from django.contrib import admin

from . import models

admin.site.register(models.Content)
admin.site.register(models.Version)
