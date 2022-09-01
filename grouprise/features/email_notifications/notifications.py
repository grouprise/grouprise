import datetime
import email.utils
import hashlib
import os
import uuid
from email.utils import formatdate

import django
import django.utils.timezone
from django.apps import apps
from django.conf import settings
from django.core import mail
from django.db import models
from django.template import loader
from django.urls import reverse

from grouprise.core.models import PermissionToken
from grouprise.core.settings import CORE_SETTINGS, get_grouprise_site
from grouprise.core.templatetags.defaultfilters import full_url as build_absolute_uri
from grouprise.core.templatetags.defaulttags import ref
from grouprise.features.associations.models import Association
from grouprise.features.content.models import Content
from grouprise.features.contributions import models as contributions
from grouprise.features.conversations.models import Conversation
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups.models import Group
from grouprise.features.memberships import models as memberships
from grouprise.features.notifications.notifications import (
    RelatedGestalten,
    BaseNotifications,
)


class Notification:
    @classmethod
    def send_all(cls, instance, force=False, **extra_kwargs):
        for recipient, kwargs in cls.get_recipients(instance).items():
            if (force or not recipient.is_email_blocker) and (
                recipient.id != CORE_SETTINGS.FEED_IMPORTER_GESTALT_ID
            ):
                kwargs.update(extra_kwargs)
                cls(instance).send(recipient, **kwargs)

    def __init__(self, instance):
        self.object = instance
        self.site = get_grouprise_site()

    def create_token(self):
        token = PermissionToken(
            feature_key="notification-reply", gestalt=self.recipient
        )
        token.target = self.object
        token.save()
        return token

    def get_attachments(self):
        """
        Return a list of filenames to use as attachments.
        """
        return []

    def get_body(self):
        context = self.get_context_data()
        template = loader.get_template(self.get_template_name())
        template.backend.engine.autoescape = False
        return template.render(context)

    def get_context_data(self, **kwargs):
        kwargs["object"] = self.object
        kwargs["recipient"] = self.recipient
        kwargs["site"] = self.site
        kwargs["url"] = self.url
        kwargs.update(self.kwargs)
        return kwargs

    def get_date(self):
        return formatdate(localtime=True)

    def get_formatted_recipient(self):
        return "{} <{}>".format(self.recipient, self.recipient.user.email)

    def get_formatted_reply_address(self, token):
        return "<{}>".format(
            CORE_SETTINGS.DEFAULT_REPLY_TO_EMAIL.format(reply_key=token.secret_key)
        )

    def get_formatted_sender(self):
        sender = self.get_sender()
        name = "{} via ".format(sender) if sender else ""
        if sender:
            email = CORE_SETTINGS.DEFAULT_DISTINCT_FROM_EMAIL.format(slug=sender.slug)
        else:
            email = settings.DEFAULT_FROM_EMAIL
        from_email = "{name}{site} <{email}>".format(
            name=name, site=self.site.name, email=email
        )
        return from_email

    def get_headers(self, **kwargs):
        # thread headers
        kwargs.update(self.get_thread_headers())

        # reply-to with token
        token = self.get_reply_token()
        if token:
            kwargs["Reply-To"] = self.get_formatted_reply_address(token)

        # archived-at with url
        self.url = self.get_url()
        if self.url:
            kwargs["Archived-At"] = "<{}>".format(build_absolute_uri(self.url))

        # list-id
        list_id = self.get_list_id()
        if list_id:
            kwargs["List-Id"] = list_id

        return kwargs

    def get_list_id(self):
        return None

    def get_message(self):
        headers = self.get_headers(Date=self.get_date())
        subject_prefix = "Re: " if self.is_reply() else ""
        subject_context = self.get_subject_context()
        if subject_context:
            subject_prefix += "[{}] ".format(subject_context)
        subject = subject_prefix + self.get_subject()
        return mail.EmailMessage(
            body=self.get_body(),
            from_email=self.get_formatted_sender(),
            headers=headers,
            subject=subject,
            to=[self.get_formatted_recipient()],
        )

    def get_message_ids(self):
        """generate a unique message ID for this specific email message and related IDs

        Most notification subclasses should implement their own specific message ID generator.
        Some notifications lack unique features, since they can be issued multiple times (e.g.
        group recommendations or membership associations).
        In these cases we pick a random ID. These subclasses do not need to overwrite this method.

        The result is a tuple of three items:
            * unique message ID
            * parent message ID (if available)
            * thread ID and other related messages (if available)
        """
        now_string = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        uuid_string = uuid.uuid4().hex[:16]
        my_id = "{}.{}".format(now_string, uuid_string)
        return my_id, None, []

    def get_reply_token(self):
        return None

    def get_sender(self):
        return None

    def get_subject(self):
        return self.subject

    def get_subject_context(self):
        return None

    def get_template_name(self):
        app_label = apps.get_containing_app_config(type(self).__module__).label
        return "{}/{}.txt".format(app_label, type(self).__name__.lower())

    def get_thread_headers(self):
        def format_message_id(message_id, recipient):
            try:
                # The reference towards the recipient is not a security measure, thus
                # collisions (due the capping of 16 bytes) are acceptable.
                recipient_token = hashlib.sha256(
                    recipient.user.email.encode("utf-8")
                ).hexdigest()[:16]
                return "<{}-{}@{}>".format(
                    message_id, recipient_token, self.site.domain
                )
            except AttributeError:
                return "<{}@{}>".format(message_id, self.site.domain)

        headers = {}
        message_id, parent_id, reference_ids = self.get_message_ids()
        headers["Message-ID"] = format_message_id(message_id, self.recipient)
        if parent_id:
            headers["In-Reply-To"] = format_message_id(parent_id, self.recipient)
            if parent_id not in reference_ids:
                reference_ids.append(parent_id)
        if reference_ids:
            headers["References"] = " ".join(
                [format_message_id(ref_id, self.recipient) for ref_id in reference_ids]
            )
        return headers

    def get_url(self):
        return None

    def is_reply(self):
        return False

    def send(self, recipient, **kwargs):
        self.recipient = recipient
        self.kwargs = kwargs

        # construct message
        message = self.get_message()

        # add attachments
        for file_name in self.get_attachments():
            message.attach_file(file_name)

        # we don't expect errors when sending mails because we just pass mails to django-mailer
        message.send()


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


class EmailNotifications(BaseNotifications):
    def does_recipient_want_notifications(self, recipient: Gestalt):
        return recipient.receives_email_notifications

    def get_notification_class(self):
        if isinstance(self.related_gestalten.instance, Content):
            return ContentCreated
        else:
            return ContributionCreated

    def send(self):
        kwargs = {"association": self.related_gestalten.association}
        if self.related_gestalten.is_public_context:
            self.send_to(
                RelatedGestalten.Audience.GROUP_SUBSCRIBERS,
                is_subscriber=True,
                **kwargs,
            )
        else:
            self.send_to(
                RelatedGestalten.Audience.SUBSCRIBED_GROUP_MEMBERS,
                is_subscriber=True,
                **kwargs,
            )
        self.send_to(RelatedGestalten.Audience.ASSOCIATED_GESTALT, **kwargs)
        self.send_to(RelatedGestalten.Audience.EXTERNAL_INITIAL_CONTRIBUTOR, **kwargs)
