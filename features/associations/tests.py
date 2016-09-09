from core import tests
from entities import models
from features.comments import tests as comments
from features.content import tests as content
from features.gestalten import tests as gestalten
from features.groups import tests as groups
from features.memberships import test_mixins as memberships


class GroupAssociatedContentMixin(groups.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.GroupContent.objects.create(
                content=cls.content, group=cls.group)


class OtherGestaltAssociatedContentMixin(gestalten.OtherGestaltMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.GestaltContent.objects.create(
                content=cls.content, gestalt=cls.other_gestalt)


class CommentOtherGestaltAssociatedContent(
        comments.NotificationToOtherGestalt,
        OtherGestaltAssociatedContentMixin, content.ContentMixin, tests.Test):
    """
    If a gestalt authors a comment to content associated with another gestalt
    * a notification is sent to the other gestalt.
    """


class CommentGroupAssociatedContent(
        comments.NotificationToOtherGestalt,
        GroupAssociatedContentMixin, memberships.OtherMemberMixin,
        content.ContentMixin, tests.Test):
    """
    If a gestalt authors a comment to content associated with a group
    * a notification is sent to group members.
    """
