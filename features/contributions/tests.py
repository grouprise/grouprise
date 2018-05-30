import django
from django.urls import reverse

import features.articles.tests
from . import models


class ContributionMixin(features.articles.tests.ArticleMixin):
    def create_contribution(self):
        self.client.post(
                reverse('content', args=[self.association.entity.slug, self.association.slug]),
                {'text': 'Test Comment'})
        return models.Contribution.objects.get(text__text='Test Comment')

    def setUp(self):
        super().setUp()
        self.contribution = self.create_contribution()


class Delete(ContributionMixin, django.test.TestCase):
    def test_delete_contribution(self):
        delete_url = reverse(
                'delete-contribution',
                args=[
                    self.association.entity.slug, self.association.slug, self.contribution.pk])
        article_url = reverse(
                'content', args=[self.association.entity.slug, self.association.slug])

        # article contains comment
        r = self.client.get(article_url)
        self.assertContains(r, 'Test Comment')

        # find delete link on article page
        self.assertContains(r, 'href="{}"'.format(delete_url))

        # get delete confirmation page
        r = self.client.get(delete_url)
        self.assertEqual(r.status_code, 200)

        # delete comment
        r = self.client.post(delete_url)
        self.assertRedirects(r, article_url)

        # article contains comment
        r = self.client.get(article_url)
        self.assertNotContains(r, 'Test Comment')
