from django.db.models.signals import post_save
from django.dispatch import receiver

from grouprise.features.groups import models as groups
from . import models, notifications


@receiver(post_save, sender=groups.Group)
def add_first_member(sender, instance, created, **kwargs):
    if created:
        group = instance
        if group.gestalt_created:
            models.Membership.objects.create(
                    created_by=group.gestalt_created,
                    group=group, member=group.gestalt_created)


@receiver(post_save, sender=models.Membership)
def send_membership_notification(sender, instance, created, **kwargs):
    if created:
        membership = instance
        if membership.created_by != membership.member:
            notifications.MembershipCreated(membership).send(membership.member)
