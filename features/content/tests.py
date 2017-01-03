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

import entities.models
from content import models
from features.gestalten import tests as gestalten


# class GroupAssociatedContentMixin(groups.GroupMixin):
#     @classmethod
#     def setUpTestData(cls):
#         super().setUpTestData()
#         models.GroupContent.objects.create(
#                 content=cls.content, group=cls.group)


# class OtherGestaltAssociatedContentMixin(gestalten.OtherGestaltMixin):
#     @classmethod
#     def setUpTestData(cls):
#         super().setUpTestData()
#         models.GestaltContent.objects.create(
#                 content=cls.content, gestalt=cls.other_gestalt)


class ContentMixin(gestalten.GestaltMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        article = models.Article.objects.create(
                author=cls.gestalt, text='Test', title='Test', public=True)
        cls.content = models.Content.objects.get(article=article)


class NoAuthorContentMixin(
        gestalten.AuthenticatedMixin, gestalten.OtherGestaltMixin,
        ContentMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content.author = cls.other_gestalt
        cls.content.save()


class OtherCommentedMixin(ContentMixin, gestalten.OtherGestaltMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Comment.objects.create(
                author=cls.other_gestalt, content=cls.content,
                text='Other Text')


# class NoNotification:
#     def test_comment_no_notification(self):
#         models.Comment.objects.create(
#                 author=self.other_gestalt, content=self.content, text='Test')
#         self.assertNoNotificationSent()


class NotificationToOtherGestalt:
    def test_comment_notification(self):
        models.Comment.objects.create(
                author=self.gestalt, content=self.content, text='Test')
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.other_gestalt)


class NoNotification:
    def test_content_creation(self):
        content = models.Article.objects.create(
                author=self.other_gestalt, title='Test Content')
        entities.models.GroupContent.objects.create(content=content, group=self.group)
        self.assertNoNotificationSent()


# class CommentContent(
#         NotificationToOtherGestalt,
#         NoAuthorContentMixin, tests.Test):
#     """
#     If a gestalt comments on other gestaltens' content:
#     * a notification is sent to the content author.
#     """


# class CommentCommentedContent(
#         NotificationToOtherGestalt,
#         OtherCommentedMixin, tests.Test):
#     """
#     If a gestalt comments on content commented by another gestalt:
#     * a notification is sent to the other gestalt.
#     """


# class CommentOtherGestaltAssociatedContent(
#         NotificationToOtherGestalt,
#         OtherGestaltAssociatedContentMixin, content.ContentMixin, tests.Test):
#     """
#     If a gestalt authors a comment to content associated with another gestalt
#     * a notification is sent to the other gestalt.
#     """


# class CommentGroupAssociatedContent(
#         NotificationToOtherGestalt,
#         GroupAssociatedContentMixin, memberships.OtherMemberMixin,
#         content.ContentMixin, tests.Test):
#     """
#     If a gestalt authors a comment to content associated with a group
#     * a notification is sent to group members.
#     """
