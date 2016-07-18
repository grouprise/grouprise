from django.db import models


class Membership(models.Model):
    date_joined = models.DateField(auto_now_add=True)
    group = models.ForeignKey('entities.Group')
    member = models.ForeignKey('entities.Gestalt')

    class Meta:
        unique_together = ('group', 'member')
