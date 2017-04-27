import core.tests
from features.associations import models as associations
from features.contributions import models as contributions
from features.gestalten import tests as gestalten
from features.memberships import test_mixins as memberships


class ArticleMixin(gestalten.AuthenticatedMixin):
    def create_article(self, **kwargs):
        kwargs.update({'title': 'Test', 'text': 'Test'})
        self.client.post(self.get_url('create-article'), kwargs)
        return associations.Association.objects.get(content__title='Test')

    def get_content_url(self):
        return self.get_url('content', (self.association.entity.slug, self.association.slug))

    def setUp(self):
        super().setUp()
        self.association = self.create_article()


class GroupArticleMixin(ArticleMixin):
    def create_article(self, **kwargs):
        kwargs.update({'title': 'Group Article', 'text': 'Test'})
        self.client.post(self.get_url('create-group-article', self.group.slug), kwargs)
        return associations.Association.objects.get(content__title='Group Article')


class Guest(memberships.MemberMixin, core.tests.Test):
    def create_article(self, **kwargs):
        self.client.force_login(self.gestalt.user)
        kwargs.update({'title': 'Test', 'text': 'Test'})
        self.client.post(self.get_url('create-article'), kwargs)
        self.client.logout()

    def get_article_url(self):
        return associations.Association.objects.get(content__title='Test').get_absolute_url()

    def create_group_article(self, **kwargs):
        self.client.force_login(self.gestalt.user)
        kwargs.update({'title': 'Group Article', 'text': 'Test'})
        self.client.post(self.get_url('create-group-article', self.group.slug), kwargs)
        self.client.logout()

    def get_group_article_url(self):
        return associations.Association.objects.get(
                content__title='Group Article').get_absolute_url()

    def test_guest_article_link(self):
        self.assertNotContainsLink(self.client.get('/'), self.get_url('create-article'))
        self.assertNotContainsLink(
                self.client.get(self.get_url('articles')), self.get_url('create-article'))
        self.assertNotContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_url('create-article'))
        self.assertNotContainsLink(
                self.client.get(self.group.get_absolute_url()), self.get_url('create-article'))

    def test_guest_create_article(self):
        self.assertLogin(url_name='create-article')
        self.assertLogin(url_name='create-article', method='post')

    def test_guest_create_group_article(self):
        self.assertLogin(url_name='create-group-article', url_args=[self.group.slug])
        self.assertLogin(
                url_name='create-group-article', url_args=[self.group.slug], method='post')

    def test_guest_public_article(self):
        self.create_article(public=True)
        self.assertContainsLink(self.client.get('/'), self.get_article_url())
        self.assertContainsLink(
                self.client.get(self.get_url('articles')), self.get_article_url())
        self.assertContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_article_url())
        self.assertOk(url=self.get_article_url())

    def test_guest_internal_article(self):
        self.create_article(public=False)
        self.assertNotContainsLink(self.client.get('/'), self.get_article_url())
        self.assertNotContainsLink(
                self.client.get(self.get_url('articles')), self.get_article_url())
        self.assertNotContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_article_url())
        self.assertLogin(url=self.get_article_url())

    def test_guest_public_group_article(self):
        self.create_group_article(public=True)
        self.assertContainsLink(obj=self.group, link_url=self.get_group_article_url())
        self.assertOk(url=self.get_group_article_url())
        self.assertLogin(url=self.get_group_article_url(), method='post')

    def test_guest_internal_group_article(self):
        self.create_group_article(public=False)
        self.assertNotContainsLink(obj=self.group, link_url=self.get_group_article_url())
        self.assertLogin(url=self.get_group_article_url())
        self.assertLogin(url=self.get_group_article_url(), method='post')


class Gestalt(memberships.AuthenticatedMemberMixin, core.tests.Test):
    def create_article(self, **kwargs):
        kwargs.update({'title': 'Test', 'text': 'Test'})
        return self.client.post(self.get_url('create-article'), kwargs)

    def create_group_article(self, **kwargs):
        kwargs.update({'title': 'Group Article', 'text': 'Test'})
        return self.client.post(self.get_url('create-group-article', self.group.slug), kwargs)

    def get_article_url(self):
        return associations.Association.objects.get(content__title='Test').get_absolute_url()

    def get_group_article_url(self):
        return associations.Association.objects.get(
                content__title='Group Article').get_absolute_url()

    def test_gestalt_article_link(self):
        self.assertContainsLink(self.client.get('/'), self.get_url('create-article'))
        self.assertContainsLink(
                self.client.get(self.get_url('articles')), self.get_url('create-article'))
        self.assertContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_url('create-article'))
        self.assertContainsLink(self.client.get(self.group.get_absolute_url()), self.get_url(
            'create-group-article', self.group.slug))

    def test_gestalt_create_article(self):
        self.assertEqual(self.client.get(self.get_url('create-article')).status_code, 200)
        response = self.create_article()
        self.assertRedirects(response, self.get_article_url())
        self.assertExists(associations.Association, content__title='Test')

    def test_gestalt_create_group_article(self):
        self.assertEqual(self.client.get(self.get_url(
            'create-group-article', self.group.slug)).status_code, 200)
        response = self.create_group_article()
        self.assertRedirects(response, self.get_group_article_url())
        self.assertExists(associations.Association, content__title='Group Article')

    def test_gestalt_public_article(self):
        self.create_article(public=True)
        self.assertContainsLink(self.client.get('/'), self.get_article_url())
        self.assertContainsLink(
                self.client.get(self.get_url('articles')), self.get_article_url())
        self.assertContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_article_url())
        self.assertOk(url=self.get_article_url())

    def test_gestalt_internal_article(self):
        self.create_article(public=False)
        self.assertContainsLink(self.client.get('/'), self.get_article_url())
        self.assertContainsLink(
                self.client.get(self.get_url('articles')), self.get_article_url())
        self.assertContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_article_url())
        self.assertOk(url=self.get_article_url())

    def test_gestalt_public_group_article(self):
        self.create_group_article(public=True)
        self.assertContainsLink(obj=self.group, link_url=self.get_group_article_url())
        self.assertOk(url=self.get_group_article_url())

    def test_gestalt_internal_group_article(self):
        self.create_group_article(public=False)
        self.assertContainsLink(obj=self.group, link_url=self.get_group_article_url())
        self.assertOk(url=self.get_group_article_url())

    def test_gestalt_comment_article(self):
        self.create_article()
        self.assertRedirect(
                url=self.get_article_url(), method='post', data={'text': 'Comment'})
        self.assertExists(contributions.Contribution, text__text='Comment')


class GestaltAndArticle(ArticleMixin, core.tests.Test):
    def create_comment(self, **kwargs):
        kwargs.update({'text': 'Comment'})
        return self.client.post(self.get_content_url(), kwargs)

    def test_comment_self_notified(self):
        self.create_comment()
        self.assertNotificationsSent(1)
        self.assertNotificationRecipient(self.gestalt)
        self.assertNotificationContains(self.get_content_url())
        self.assertNotificationContains('Comment')


class TwoGestaltenAndGroupArticle(
        GroupArticleMixin, memberships.OtherMemberMixin, memberships.AuthenticatedMemberMixin,
        core.tests.Test):
    def create_comment(self, **kwargs):
        kwargs.update({'text': 'Comment'})
        return self.client.post(self.get_content_url(), kwargs)

    def test_comment_both_notified(self):
        self.create_comment()
        self.assertNotificationsSent(2)
        self.assertNotificationRecipient(self.other_gestalt)
