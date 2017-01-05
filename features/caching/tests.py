from core import tests
from django.conf import settings
from django.core import cache
from features.gestalten import tests as gestalten
from features.groups import tests as groups


class Caching(gestalten.GestaltMixin, groups.GroupMixin, tests.Test):
    def change_slug(self, slug):
        self.group.slug = slug
        self.group.save()

    def test(self):
        self.disable_caching()
        self.change_slug('new_slug')
        ref_response = self.client.get(self.get_url('group-index'))

        self.change_slug('old_slug')
        self.enable_caching()
        self.client.get(self.get_url('group-index'))
        self.change_slug('new_slug')
        response = self.client.get(self.get_url('group-index'))

        self.assertEquals(response.content, ref_response.content)
