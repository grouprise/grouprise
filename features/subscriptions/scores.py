from . import models
from features.memberships import scores as memberships


class Group(memberships.Group):
    @classmethod
    def get_num_gestalten(cls, group):
        return models.Subscription.objects.filter(subscribed_to=group).count()

    @classmethod
    def get_queryset(cls, group):
        return super().get_queryset(group).filter(content__public=True)
