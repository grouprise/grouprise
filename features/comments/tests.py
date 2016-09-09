from content import models as comments
from core import tests
from features.subscriptions import test_mixins as subscriptions


class NotificationToOtherGestalt:
    def test_comment(self):
        comments.Comment.objects.create(
                author=self.gestalt, content=self.content, text='Test')
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.other_gestalt)


class OtherSubscriber(
        NotificationToOtherGestalt,
        subscriptions.OtherContentSubscriberMixin, tests.Test):
    """
    If an author creates a comment
    * a notification to content subscribers should be sent.
    """
