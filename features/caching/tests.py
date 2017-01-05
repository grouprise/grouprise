from core import tests
from features.groups import tests as groups


class Caching(groups.GroupMixin, tests.Test):
    def test_group_slug(self):
        self.enable_caching()
        ref_response = self.client.get(self.get_url('group-index'))
        self.group.slug = 'new_slug'
        self.group.save()
        response = self.client.get(self.get_url('group-index'))
        self.assertNotEquals(response.content, ref_response.content)
