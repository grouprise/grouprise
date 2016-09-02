from . import models
from entities import models as entities
from features.associations import notifications as associations


class ContentAssociated(associations.ContentAssociated):
    def get_recipients(self):
        recipients = super().get_recipients()
        if (type(self.association) == entities.GroupContent
                and self.content.public):
            subscriptions = models.Subscription.objects.filter(
                    subscribed_to=self.association.group)
            recipients.update(entities.Gestalt.objects.filter(
                    subscription__in=subscriptions))
            recipients.discard(self.content.author)
        return recipients
