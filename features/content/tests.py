import django

import core.tests


class TestUrls(core.tests.Test):
    def test_content_404(self):
        r = self.client.get(django.urls.reverse(
            'content', args=['non-existent', 'non-existent']))
        self.assertEqual(r.status_code, 404)
        r = self.client.get(self.get_url('content-permalink', 0))
        self.assertEqual(r.status_code, 404)
        r = self.client.get(django.urls.reverse(
            'update-content', args=['non-existent', 'non-existent']))
        self.assertEqual(r.status_code, 404)
