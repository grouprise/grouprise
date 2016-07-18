from django.db import models


class Membership(models.Model):
    date_joined = models.DateField(auto_now_add=True)
    gestalt = models.ForeignKey('entities.Gestalt')
    group = models.ForeignKey('entities.Group')

    class Meta:
        unique_together = ('gestalt', 'group')
