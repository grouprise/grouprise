from . import models
from django.contrib.contenttypes import models as contenttypes
from features.conversations import models as conversations
from features.memberships import scores as memberships


class Group(memberships.Group):
    @classmethod
    def get_associations(cls, group):
        return super().get_associations(group).exclude(
                container_type=contenttypes.ContentType.objects.get_for_model(
                    conversations.Conversation))

    @classmethod
    def get_num_gestalten(cls, group):
        return models.Subscription.objects.filter(subscribed_to=group).count()

    @classmethod
    def get_groupcontent(cls, group):
        return super().get_groupcontent(group).filter(content__public=True)
