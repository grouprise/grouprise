import core.tests


class TestUrls(core.tests.Test):
    def test_stadt_404(self):
        r = self.client.get(self.get_url('entity', 'non-existent'))
        self.assertEqual(r.status_code, 404)
