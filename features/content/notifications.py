import core
from features.groups.models import Group
from feaures.subscriptions.notifications import update_recipients


class ContentCreated(core.notifications.Notification):
    @classmethod
    def get_recipients(cls, content):
        recipients = {}
        # send notifications to groups associated with content (instance)
        associations = content.associations.filter(entity_type=Group.content_type)
        for association in associations:
            # all subscribers receive a notification
            subscriptions = association.entity.subscriptions.all()
            if not association.public:
                # for internal content, only subscribed members receive a notification
                subscriptions = subscriptions.filter(
                        subscriber__memberships__group=association.entity)
            update_recipients(recipients, association=association, subscriptions=subscriptions)
        return recipients

    def get_message_ids(self):
        return self.object.get_unique_id(), None, []

    def get_reply_token(self):
        return self.create_token()

    def get_sender(self):
        if (self.group
                and not self.recipient.user.has_perm('memberships.view_list', self.group)):
            return self.group
        else:
            return self.object.versions.last().author

    def get_subject(self):
        return self.object.subject

    def get_template_name(self):
        if self.object.is_gallery:
            name = 'galleries/created.txt'
        elif self.object.is_file:
            name = 'files/created.txt'
        elif self.object.is_poll:
            name = 'polls/created.txt'
        elif self.object.is_event:
            name = 'events/created.txt'
        else:
            name = 'articles/created.txt'
        return name
