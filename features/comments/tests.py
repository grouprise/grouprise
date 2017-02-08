from content import models
from core import tests
from features.content import tests as content
from features.gestalten import tests as gestalten


class OtherCommentedMixin(content.ContentMixin, gestalten.OtherGestaltMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Comment.objects.create(
                author=cls.other_gestalt, content=cls.content,
                text='Other Text')


class NoNotification:
    def test_comment_no_notification(self):
        models.Comment.objects.create(
                author=self.other_gestalt, content=self.content, text='Test')
        self.assertNoNotificationSent()


class NotificationToOtherGestalt:
    def test_comment_notification(self):
        models.Comment.objects.create(
                author=self.gestalt, content=self.content, text='Test')
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.other_gestalt)


class CommentContent(
        NotificationToOtherGestalt,
        content.NoAuthorContentMixin, tests.Test):
    """
    If a gestalt comments on other gestaltens' content:
    * a notification is sent to the content author.
    """


class CommentCommentedContent(
        NotificationToOtherGestalt,
        OtherCommentedMixin, tests.Test):
    """
    If a gestalt comments on content commented by another gestalt:
    * a notification is sent to the other gestalt.
    """
