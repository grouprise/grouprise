from django.db import models


class Imported(models.Model):
    key = models.CharField(max_length=255)
