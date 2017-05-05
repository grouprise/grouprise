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

from . import views
from allauth.account import views as allauth_views
from django.conf import urls

urlpatterns = [
    urls.url(
        r'^confirm/(?P<key>[-:\w]+)/$',
        views.Confirm.as_view(),
        name='account_confirm_email'),
    urls.url(r'^email/$', views.Email.as_view(), name='account_email'),
    urls.url(r'^login/$', views.Login.as_view(), name='account_login'),
    urls.url(r'^logout/$', views.Logout.as_view(), name='account_logout'),
    urls.url(
        r'^password/change/$',
        views.PasswordChange.as_view(),
        name='account_change_password'),
    urls.url(
        r'^password/reset/$',
        views.PasswordReset.as_view(),
        name='account_reset_password'),
    urls.url(
        r'^password/reset/done/$',
        views.PasswordResetDone.as_view(),
        name='account_reset_password_done'),
    urls.url(
        r'^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$',
        views.PasswordResetFromKey.as_view(),
        name='account_reset_password_from_key'),
    urls.url(
        r'^password/reset/key/done/$',
        allauth_views.password_reset_from_key_done,
        name='account_reset_password_from_key_done'),
    urls.url(
        r'^signup/$',
        views.Signup.as_view(),
        name='account_signup'),
]
