import email.utils
import os

import django
import django.utils.timezone
from django.db import models
from django.urls import reverse

from grouprise.core.notifications import Notification
from grouprise.core.templatetags.defaulttags import ref
from grouprise.features.associations.models import Association
from grouprise.features.content.models import Content
from grouprise.features.contributions import models as contributions
from grouprise.features.conversations.models import Conversation
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups.models import Group
from grouprise.features.memberships import models as memberships


class ContentOrContributionCreated(Notification):
    @staticmethod
    def get_recipients(contentOrContribution: models.Model) -> dict:
        if isinstance(contentOrContribution, Content):
            container = contentOrContribution
        else:
            container = contentOrContribution.container
        recipients = {}
        association: Association
        for association in container.associations.all():
            if association.public:
                # for public associations we just send notifications to all group subscribers
                if isinstance(association.entity, Group):
                    recipients.update(
                        {
                            subscriber: {"is_subscriber": True}
                            for subscriber in association.entity.subscribers.all()
                        }
                    )
            else:
                # for private associations
                if isinstance(association.entity, Group):
                    # we send notifications to subscribed group members
                    recipients.update(
                        {
                            subscriber: {"is_subscriber": True}
                            for subscriber in association.entity.members.filter(
                                subscriptions__group=association.entity
                            )
                        }
                    )
                elif isinstance(association.entity, Gestalt):
                    # we send a notification to the associated gestalt
                    recipients[association.entity] = {}
                # for conversations we check the initiating contribution
                if (
                    isinstance(container, Conversation)
                    and container.contributions.exists()
                ):
                    initiating_gestalt: Gestalt = container.contributions.first().author
                    # if either the conversation is private (associated to a gestalt) or the
                    # initial author is not a group member, they get notified
                    if isinstance(association.entity, Gestalt) or (
                        isinstance(association.entity, Group)
                        and not association.entity.members.filter(
                            pk=initiating_gestalt.pk
                        ).exists()
                    ):
                        recipients[initiating_gestalt] = {}
            # enrich recipients with some context
            recipients.update(
                {
                    recipient: {"association": association, **context}
                    for recipient, context in recipients.items()
                }
            )
        return recipients

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
