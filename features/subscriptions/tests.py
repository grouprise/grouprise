import core.tests
from features.associations import models as associations
from features.memberships import test_mixins as memberships
from features.subscriptions import test_mixins as subscriptions


class MemberAndSubscriber(
        subscriptions.OtherGroupSubscriberMixin, memberships.AuthenticatedMemberMixin,
        core.tests.Test):

    def create_article(self, **kwargs):
        kwargs.update({'public': True, 'title': 'Group Article', 'text': 'Test'})
        self.client.post(self.get_url('create-group-article', self.group.slug), kwargs)
        self.association = associations.Association.objects.get(content__title='Group Article')

    def test_subscriber_article_notified(self):
        self.create_article()
        self.assertNotificationsSent(2)
        self.assertNotificationRecipient(self.other_gestalt)
