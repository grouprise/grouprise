from django.test import TestCase

from grouprise.features.rest_api.frontend.filters import GroupFilter
from grouprise.features.groups.tests.mixins import GroupMixin


class GroupFilterTestCase(GroupMixin, TestCase):
    """ verify the group filter used for queries like /stadt/api/groups?name=foo """

    def _assert_match(self, filter_dict: dict) -> None:
        self.assertIn(self.group, GroupFilter(filter_dict).qs)

    def _assert_not_match(self, filter_dict: dict) -> None:
        self.assertNotIn(self.group, GroupFilter(filter_dict).qs)

    def test_matches(self) -> None:
        for filter_dict in (
            {"name": self.group.name},
            {"name": self.group.name[2:-3]},
            {"name": self.group.name.lower()},
            {"name": self.group.name.upper()},
            {"name": self.group.name.upper()},
            {"slug": self.group.slug},
            {"id": str(self.group.pk)},
            {"name": self.group.name, "id": str(self.group.pk)},
        ):
            with self.subTest(filter_dict=filter_dict):
                self._assert_match(filter_dict)

    def test_not_matches(self) -> None:
        for filter_dict in (
            {"name": self.group.name + "x"},
            {"slug": self.group.slug[1:]},
            {"id": str(self.group.pk + 1)},
            # combination of success and failure
            {"name": self.group.name, "id": str(self.group.pk + 1)},
            # reverse combination of success and failure
            {"name": self.group.name + "x", "id": str(self.group.pk)},
        ):
            with self.subTest(filter_dict=filter_dict):
                self._assert_not_match(filter_dict)
