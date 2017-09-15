import django
from django.core.urlresolvers import reverse

import features.articles.tests


class Create(features.articles.tests.ArticleMixin, django.test.TestCase):
    def test_note_creation(self):
        note_text = 'Test Note'
        creation_url = reverse(
                'create-note', args=(self.association.entity.slug, self.association.slug))

        # article page contains note creation link
        r = self.client.get(self.association.get_absolute_url())
        self.assertContains(r, 'href="{}"'.format(creation_url))

        # note creation form renders successfully
        r = self.client.get(creation_url)
        self.assertEqual(r.status_code, 200)

        # note gets created
        r = self.client.post(creation_url, {'text': note_text})
        self.assertRedirects(r, self.association.get_absolute_url())

        # board contains note
        r = self.client.get(reverse('index'))
        self.assertContains(r, note_text)
