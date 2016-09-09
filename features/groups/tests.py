from entities import models as entities_models


class GroupMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.group = entities_models.Group.objects.create(name='Test')


class ClosedGroupMixin(GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.group.closed = True
        cls.group.save()
