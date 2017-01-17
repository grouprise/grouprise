from django.db import models


class Membership(models.Model):
    created_by = models.ForeignKey(
            'gestalten.Gestalt', related_name='memberships_created')
    date_joined = models.DateField(auto_now_add=True)
    group = models.ForeignKey('groups.Group', related_name='memberships')
    member = models.ForeignKey('gestalten.Gestalt', related_name='memberships')

    def __str__(self):
        return "%s is member of %s since %s" % (
            str(self.member.user.get_username()),
            str(self.group.slug), str(self.date_joined)
        )

    class Meta:
        unique_together = ('group', 'member')
