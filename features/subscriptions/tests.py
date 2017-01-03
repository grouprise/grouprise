"""
This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.
"""

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
