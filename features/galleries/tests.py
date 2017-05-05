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

import core.tests
from features.associations import models as associations
from features.contributions import models as contributions
from features.images import tests as images
from features.memberships import test_mixins as memberships


class Guest(images.ImageMixin, memberships.MemberMixin, core.tests.Test):
    def create_gallery(self, **kwargs):
        self.client.force_login(self.gestalt.user)
        kwargs.update({'title': 'Test', 'text': 'Test', 'images': [self.image.pk]})
        self.client.post(self.get_url('create-gallery'), kwargs)
        self.client.logout()

    def get_gallery_url(self):
        return associations.Association.objects.get(content__title='Test').get_absolute_url()

    def create_group_gallery(self, **kwargs):
        self.client.force_login(self.gestalt.user)
        kwargs.update({'title': 'Group Gallery', 'text': 'Test', 'images': [self.image.pk]})
        self.client.post(self.get_url('create-group-gallery', self.group.slug), kwargs)
        self.client.logout()

    def get_group_gallery_url(self):
        return associations.Association.objects.get(
                content__title='Group Gallery').get_absolute_url()

    def test_guest_gallery_link(self):
        self.assertNotContainsLink(self.client.get('/'), self.get_url('create-gallery'))
        self.assertNotContainsLink(
                self.client.get(self.get_url('articles')), self.get_url('create-gallery'))
        self.assertNotContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_url('create-gallery'))
        self.assertNotContainsLink(
                self.client.get(self.group.get_absolute_url()), self.get_url('create-gallery'))

    def test_guest_create_gallery(self):
        self.assertLogin(url_name='create-gallery')
        self.assertLogin(url_name='create-gallery', method='post')

    def test_guest_create_group_gallery(self):
        self.assertLogin(url_name='create-group-gallery', url_args=[self.group.slug])
        self.assertLogin(
                url_name='create-group-gallery', url_args=[self.group.slug], method='post')

    def test_guest_public_gallery(self):
        self.create_gallery(public=True)
        self.assertContainsLink(self.client.get('/'), self.get_gallery_url())
        self.assertContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_gallery_url())
        self.assertOk(url=self.get_gallery_url())

    def test_guest_internal_gallery(self):
        self.create_gallery(public=False)
        self.assertNotContainsLink(self.client.get('/'), self.get_gallery_url())
        self.assertNotContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_gallery_url())
        self.assertLogin(url=self.get_gallery_url())

    def test_guest_public_group_gallery(self):
        self.create_group_gallery(public=True)
        self.assertContainsLink(obj=self.group, link_url=self.get_group_gallery_url())
        self.assertOk(url=self.get_group_gallery_url())
        self.assertLogin(url=self.get_group_gallery_url(), method='post')

    def test_guest_internal_group_gallery(self):
        self.create_group_gallery(public=False)
        self.assertNotContainsLink(obj=self.group, link_url=self.get_group_gallery_url())
        self.assertLogin(url=self.get_group_gallery_url())
        self.assertLogin(url=self.get_group_gallery_url(), method='post')


class Gestalt(images.ImageMixin, memberships.AuthenticatedMemberMixin, core.tests.Test):
    def create_gallery(self, **kwargs):
        kwargs.update({'title': 'Test', 'text': 'Test', 'images': [self.image.pk]})
        return self.client.post(self.get_url('create-gallery'), kwargs)

    def create_group_gallery(self, **kwargs):
        kwargs.update({'title': 'Group Gallery', 'text': 'Test', 'images': [self.image.pk]})
        return self.client.post(self.get_url('create-group-gallery', self.group.slug), kwargs)

    def get_gallery_url(self):
        return associations.Association.objects.get(content__title='Test').get_absolute_url()

    def get_group_gallery_url(self):
        return associations.Association.objects.get(
                content__title='Group Gallery').get_absolute_url()

    def test_gestalt_gallery_link(self):
        self.assertContainsLink(self.client.get('/'), self.get_url('create-gallery'))
        self.assertContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_url('create-gallery'))
        self.assertContainsLink(self.client.get(self.group.get_absolute_url()), self.get_url(
            'create-group-gallery', self.group.slug))

    def test_gestalt_create_gallery(self):
        self.assertEqual(self.client.get(self.get_url('create-gallery')).status_code, 200)
        response = self.create_gallery()
        self.assertRedirects(response, self.get_gallery_url())
        self.assertExists(associations.Association, content__title='Test')

    def test_gestalt_create_group_gallery(self):
        self.assertEqual(self.client.get(self.get_url(
            'create-group-gallery', self.group.slug)).status_code, 200)
        response = self.create_group_gallery()
        self.assertRedirects(response, self.get_group_gallery_url())
        self.assertExists(associations.Association, content__title='Group Gallery')

    def test_gestalt_public_gallery(self):
        self.create_gallery(public=True)
        self.assertContainsLink(self.client.get('/'), self.get_gallery_url())
        self.assertContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_gallery_url())
        self.assertOk(url=self.get_gallery_url())

    def test_gestalt_internal_gallery(self):
        self.create_gallery(public=False)
        self.assertContainsLink(self.client.get('/'), self.get_gallery_url())
        self.assertContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_gallery_url())
        self.assertOk(url=self.get_gallery_url())

    def test_gestalt_public_group_gallery(self):
        self.create_group_gallery(public=True)
        self.assertContainsLink(obj=self.group, link_url=self.get_group_gallery_url())
        self.assertOk(url=self.get_group_gallery_url())

    def test_gestalt_internal_group_gallery(self):
        self.create_group_gallery(public=False)
        self.assertContainsLink(obj=self.group, link_url=self.get_group_gallery_url())
        self.assertOk(url=self.get_group_gallery_url())

    def test_gestalt_comment_gallery(self):
        self.create_gallery()
        self.assertRedirect(
                url=self.get_gallery_url(), method='post', data={'text': 'Comment'})
        self.assertExists(contributions.Contribution, text__text='Comment')
