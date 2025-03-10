from .. import models


class GroupMixin:

    group: models.Group

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.group = models.Group.objects.create(name="Test-Group")


class ClosedGroupMixin(GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.group.closed = True
        cls.group.save()
