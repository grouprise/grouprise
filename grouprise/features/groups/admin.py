import django
from django.contrib import admin

from . import models

admin.site.register(models.Group, django.contrib.gis.admin.OSMGeoAdmin)
