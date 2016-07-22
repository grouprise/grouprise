from django.db import models


class Membership(models.Model):
    date_joined = models.DateField(auto_now_add=True)
    group = models.ForeignKey('entities.Group')
    member = models.ForeignKey('entities.Gestalt', limit_choices_to={'user__is_staff': False}, verbose_name='Gestalt')

    class Meta:
        unique_together = ('group', 'member')
