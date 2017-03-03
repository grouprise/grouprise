from . import models
from entities import models as entities
from features.gestalten import models as gestalten
from features.associations import notifications as associations
import itertools


def update_recipients(recipients, associations):
    for association in associations:
        subscriptions = models.SubOrUnsubscription.objects.filter(
                subscribed_to=association.group)
        for subscription in subscriptions:
            subscription.update_gestalten(recipients, association)


class Commented(associations.Commented):
    def get_recipients(self):
        recipients = super().get_recipients()
        try:
            update_recipients(
                    recipients, [self.comment.content.groupcontent])
        except AttributeError:
            pass
        if self.comment.content.public:
            subscriptions = models.Subscription.objects.filter(
                    subscribed_to=self.comment.content)
            recipients.update(gestalten.Gestalt.objects.filter(
                    subscription__in=subscriptions))
        recipients.discard(self.comment.author)
        return recipients


class ContentAssociated(associations.ContentAssociated):
    def get_recipients(self):
        recipients = super().get_recipients()
        if type(self.association) == entities.GroupContent:
            update_recipients(recipients, [self.association])
        if (type(self.association) == entities.GroupContent
                and self.content.public):
            subscriptions = models.Subscription.objects.filter(
                    subscribed_to=self.association.group)
            subscription_recipients = gestalten.Gestalt.objects.filter(
                    subscription__in=subscriptions)
            recipients = dict(zip(recipients, itertools.repeat({'with_name': True})))
            recipients.update(
                    zip(subscription_recipients, itertools.repeat({'with_name': False})))
            if self.content.author in recipients:
                del recipients[self.content.author]
        return recipients
