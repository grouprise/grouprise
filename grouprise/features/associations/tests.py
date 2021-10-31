import django
from django.urls import reverse

import grouprise.features.articles.tests


class Delete(grouprise.features.articles.tests.ArticleMixin, django.test.TestCase):
    def test_delete_association(self):
        delete_url = reverse(
            "delete-association",
            args=[self.association.entity.slug, self.association.slug],
        )

        # index contains article
        r = self.client.get(reverse("index"))
        self.assertContains(
            r,
            'href="{}"'.format(
                reverse(
                    "content",
                    args=[self.association.entity.slug, self.association.slug],
                )
            ),
        )

        # find delete button on update page
        r = self.client.get(
            reverse(
                "update-content",
                args=[self.association.entity.slug, self.association.slug],
            )
        )
        self.assertContains(r, 'href="{}"'.format(delete_url))

        # get delete confirmation page
        r = self.client.get(delete_url)
        self.assertEqual(r.status_code, 200)

        # delete association
        r = self.client.post(delete_url)
        self.assertRedirects(r, self.association.entity.get_absolute_url())

        # index does not contain article
        r = self.client.get(reverse("index"))
        self.assertNotContains(
            r,
            'href="{}"'.format(
                reverse(
                    "content",
                    args=[self.association.entity.slug, self.association.slug],
                )
            ),
        )
