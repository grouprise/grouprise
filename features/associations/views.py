from core import fields
from features.memberships import views as memberships
from utils import views as utils_views


class ContentGroupMemberCreate(
        utils_views.GestaltMixin, memberships.MemberCreate):
    data_field_classes = (
            fields.related_object('group'),
            fields.view_object('member', key='gestalt'))
    description = (
            '<em>{{ gestalt }}</em> als Mitglied der Gruppe '
            '<em>{{ group }}</em> aufnehmen')
    permission = 'associations.create_content_group_membership'

    def get_permission_object(self):
        return self.related_object, self.get_gestalt()

    def get_view_object(self, key):
        if key == 'gestalt':
            return self.get_gestalt()
        return super().get_view_object(key)
