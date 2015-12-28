from django.contrib import admin

from . import models


admin.site.register(models.Article)
admin.site.register(models.Comment)
admin.site.register(models.Event)
admin.site.register(models.Gallery)
admin.site.register(models.Image)
