from . import models
from entities import models as entities
from features.associations import notifications as associations
import itertools


class Commented(associations.Commented):
    def get_recipients(self):
        recipients = super().get_recipients()
        if self.comment.content.public:
            subscriptions = models.Subscription.objects.filter(
                    subscribed_to=self.comment.content)
            recipients.update(entities.Gestalt.objects.filter(
                    subscription__in=subscriptions))
        recipients.discard(self.comment.author)
        return recipients


class ContentAssociated(associations.ContentAssociated):
    def get_recipients(self):
        recipients = super().get_recipients()
        if (type(self.association) == entities.GroupContent
                and self.content.public):
            subscriptions = models.Subscription.objects.filter(
                    subscribed_to=self.association.group)
            subscription_recipients = entities.Gestalt.objects.filter(
                    subscription__in=subscriptions)
            recipients = dict(zip(recipients, itertools.repeat(True)))
            recipients.update(
                    zip(subscription_recipients, itertools.repeat(False)))
            if self.content.author in recipients:
                del recipients[self.content.author]
        return recipients
