"""
Copyright 2016-2017 sense.lab e.V. <info@senselab.org>

This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.
"""

from . import models
from core import tests


class JoinAllowed:
    def test_group_join(self):
        self.assertRequest(
                methods=[tests.HTTP_GET],
                url='join', key=self.group.pk,
                response={tests.HTTP_OK})
        self.assertRequest(
                methods=[tests.HTTP_POST],
                url='join', key=self.group.pk,
                response={tests.HTTP_REDIRECTS: ('group', self.group.slug)})
        self.assertExists(
                models.Membership,
                group=self.group, member=self.gestalt)


class JoinForbidden:
    def test_group_join(self):
        self.assertRequest(
                methods=[tests.HTTP_GET, tests.HTTP_POST],
                url='join', key=self.group.pk,
                response={tests.HTTP_FORBIDDEN_OR_LOGIN})


class MemberCreateAllowedWithEmail:
    def test_member_create(self):
        self.assertRequest(
                methods=[tests.HTTP_GET],
                url='member-create', key=self.group.pk,
                response={tests.HTTP_OK})
        response = self.client.post(
                self.get_url('member-create', self.group.pk),
                {'member_email': self.other_gestalt.user.email})
        self.assertRedirects(response, self.get_url('members', self.group.pk))
        self.assertExists(
                models.Membership,
                group=self.group, member=self.other_gestalt)


class MemberCreateSendsNotification:
    def test_member_create(self):
        self.client.post(
                self.get_url('member-create', self.group.pk),
                {'member_email': self.other_gestalt.user.email})
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.other_gestalt)


class MemberCreateForbidden:
    def test_member_create(self):
        self.assertRequest(
                methods=[tests.HTTP_GET, tests.HTTP_POST],
                url='member-create', key=self.group.pk,
                response={tests.HTTP_FORBIDDEN_OR_LOGIN})


class MemberListCreateLink:
    def test_members(self):
        response = self.request(
                tests.HTTP_GET, url='members', key=self.group.pk)
        self.assertContainsLink(response, self.get_url('member-create', self.group.pk))


class MemberListNoCreateLink:
    def test_members(self):
        response = self.request(
                tests.HTTP_GET, url='members', key=self.group.pk)
        self.assertNotContainsLink(response, self.get_url('member-create', self.group.pk))


class MemberListForbidden:
    def test_members(self):
        self.assertRequest(
                methods=[tests.HTTP_GET, tests.HTTP_POST],
                url='members', key=self.group.pk,
                response={tests.HTTP_FORBIDDEN_OR_LOGIN})


class NoLink:
    def test_group(self):
        response = self.request(
                tests.HTTP_GET, url='group', key=self.group.slug)
        self.assertNotContainsLink(response, self.get_url('join', self.group.pk))
        self.assertNotContainsLink(
                response, self.get_url('resign', self.group.pk))


class OnlyJoinLink:
    def test_group(self):
        response = self.request(
                tests.HTTP_GET, url='group', key=self.group.slug)
        self.assertContainsLink(response, self.get_url('join', self.group.pk))
        self.assertNotContainsLink(
                response, self.get_url('resign', self.group.pk))


class OnlyResignLink:
    def test_group(self):
        response = self.request(
                tests.HTTP_GET, url='group', key=self.group.slug)
        self.assertNotContainsLink(response, self.get_url('join', self.group.pk))
        self.assertContainsLink(response, self.get_url('resign', self.group.pk))


class ResignAllowed:
    def test_group_resign(self):
        self.assertRequest(
                methods=[tests.HTTP_GET],
                url='resign', key=self.group.pk,
                response={tests.HTTP_OK})
        self.assertRequest(
                methods=[tests.HTTP_POST],
                url='resign', key=self.group.pk,
                response={tests.HTTP_REDIRECTS: ('group', self.group.slug)})
        self.assertNotExists(
                models.Membership,
                group=self.group, member=self.gestalt)


class ResignForbidden:
    def test_group_resign(self):
        self.assertRequest(
                methods=[tests.HTTP_GET, tests.HTTP_POST],
                url='resign', key=self.group.pk,
                response={tests.HTTP_FORBIDDEN_OR_LOGIN})
