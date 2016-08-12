from django.db import models


class Membership(models.Model):
    created_by = models.ForeignKey(
            'entities.Gestalt', related_name='memberships_created')
    date_joined = models.DateField(auto_now_add=True)
    group = models.ForeignKey('entities.Group')
    member = models.ForeignKey('entities.Gestalt', related_name='memberships')

    class Meta:
        unique_together = ('group', 'member')
