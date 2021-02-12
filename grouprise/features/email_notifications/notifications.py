import email.utils
import os

import django
import django.utils.timezone
from django.urls import reverse

from grouprise.core.notifications import Notification
from grouprise.core.templatetags.defaulttags import ref
from grouprise.features.contributions import models as contributions
from grouprise.features.groups.models import Group
from grouprise.features.memberships import models as memberships


def update_recipients(
    recipients_dict, association=None, subscriptions=[], contributions=[]
):
    def update_attributes(key, **kwargs):
        attributes = recipients_dict.setdefault(key, {})
        attributes.update((k, v) for k, v in kwargs.items() if v)

    for subscription in subscriptions:
        membership = subscription.subscriber.memberships.filter(
            group=subscription.subscribed_to
        ).first()
        update_attributes(
            subscription.subscriber,
            association=association,
            membership=membership,
            subscription=subscription,
        )
    # for contribution in contributions:
    #     update_attributes(contribution.author, contribution=contribution)
    if association and not association.entity.is_group:
        update_attributes(association.entity, association=association)


class ContentOrContributionCreated(Notification):
    def get_group(self):
        if self.association and self.association.entity.is_group:
            return self.association.entity
        else:
            return None

    def get_list_id(self):
        if self.group:
            return "<{}.{}>".format(self.group.slug, self.site.domain)
        return super().get_list_id()

    def get_message(self):
        self.association = self.kwargs.get("association")
        self.group = self.get_group()
        return super().get_message()

    def get_reply_token(self):
        return self.create_token()


class ContentCreated(ContentOrContributionCreated):
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
                    subscriber__memberships__group=association.entity
                )
            update_recipients(
                recipients, association=association, subscriptions=subscriptions
            )
        return recipients

    def get_message_ids(self):
        return self.object.get_unique_id(), None, []

    def get_sender(self):
        if self.group and not self.recipient.user.has_perm(
            "memberships.view_list", self.group
        ):
            return self.group
        else:
            return self.object.versions.last().author

    def get_subject(self):
        return self.object.subject

    def get_subject_context(self):
        if self.group:
            return self.group.slug
        else:
            return None

    def get_template_name(self):
        if self.object.is_gallery:
            name = "email_notifications/gallery_created.txt"
        elif self.object.is_file:
            name = "email_notifications/file_created.txt"
        elif self.object.is_poll:
            name = "email_notifications/poll_created.txt"
        elif self.object.is_event:
            name = "email_notifications/event_created.txt"
        else:
            name = "email_notifications/article_created.txt"
        return name

    def get_url(self):
        if self.association:
            return reverse("content-permalink", args=(self.association.pk,))
        return super().get_url()


class ContributionCreated(ContentOrContributionCreated):
    @classmethod
    def get_recipients(cls, contribution):
        recipients = {}
        # send notifications to gestalten and groups associated with content (instance)
        for association in contribution.container.associations.all():
            if association.entity.is_group:
                # subscribed members receive a notification
                subscriptions = association.entity.subscriptions.filter(
                    subscriber__memberships__group=association.entity
                )
                update_recipients(
                    recipients, association=association, subscriptions=subscriptions
                )
            else:
                # associated gestalten receive a notification
                update_recipients(recipients, association=association)
        # send notifications to contributing gestalten
        update_recipients(
            recipients, contributions=contribution.container.contributions.all()
        )
        return recipients

    def get_attachments(self):
        return [
            os.path.join(django.conf.settings.MEDIA_ROOT, c.contribution.file.name)
            for c in self.object.attachments.all()
        ]

    def get_context_data(self, **kwargs):
        if type(self.object.contribution) == contributions.Text:
            kwargs["text"] = self.object.contribution.text
        elif type(self.object.contribution) == memberships.Application:
            kwargs[
                "text"
            ] = "Ich beantrage die Mitgliedschaft in der Gruppe {}.".format(
                self.object.contribution.group
            )
        return super().get_context_data(**kwargs)

    def get_date(self):
        tz = django.utils.timezone.get_current_timezone()
        contribution_date = self.object.time_created.astimezone(tz=tz)
        return email.utils.format_datetime(contribution_date)

    def get_message_ids(self):
        my_id = self.object.get_unique_id()
        container = self.object.container
        parent_obj = self.object.in_reply_to or container
        parent_id = parent_obj.get_unique_id() if parent_obj else None
        ref_ids = []
        thread_id = container.get_unique_id()
        if thread_id != parent_id:
            ref_ids.append(thread_id)
        return my_id, parent_id, ref_ids

    def get_sender(self):
        return self.object.author

    def get_subject(self):
        return self.object.container.subject

    def get_subject_context(self):
        if self.association and self.association.entity.is_group:
            return self.association.entity.slug
        else:
            return None

    def get_template_name(self):
        if self.object.container.is_conversation:
            name = "email_notifications/conversation_contributed.txt"
        else:
            name = "email_notifications/content_contributed.txt"
        return name

    def get_url(self):
        if self.association:
            if self.object.container.is_conversation:
                return "{}#{}".format(
                    self.association.get_absolute_url(), ref(self.object)
                )
            else:
                return "{}#{}".format(
                    reverse("content-permalink", args=(self.association.pk,)),
                    ref(self.object),
                )
        return super().get_url()

    def is_reply(self):
        return not (
            self.object.container.is_conversation
            and self.object.container.contributions.first() == self.object
        )
