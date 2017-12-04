from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.http import urlencode

from core import tests
from features.gestalten import tests as gestalten
from features.gestalten.tests import AuthenticatedMixin
from .. import models


class GroupMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.group = models.Group.objects.create(name='Test-Group')


class ClosedGroupMixin(GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.group.closed = True
        cls.group.save()
