"""
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

from . import notifications
from core import fields, views
from features.groups import views as groups


class ShareGroupMixin(groups.Mixin, views.Form):
    data_field_classes = (fields.email('recipient'),)

    def get_related_object(self):
        return self.get_group()


class GroupRecommend(ShareGroupMixin):
    action = 'Gruppe empfehlen'
    message = 'Die Empfehlung wurde versendet.'
    permission_required = 'sharing.recommend_group'
    title = 'Empfehlung'

    def form_valid(self, form):
        notifications.GroupRecommend(
                group=self.related_object,
                recipient_email=form.cleaned_data['recipient_email']
                ).send()
        return super().form_valid(form)


class MemberInvite(ShareGroupMixin):
    action = 'Als Mitglied einladen'
    message = 'Die Einladung wurde versendet.'
    permission_required = 'sharing.invite_member'
    title = 'Einladung'

    def form_valid(self, form):
        notifications.MemberInvite(
                group=self.related_object,
                recipient_email=form.cleaned_data['recipient_email']
                ).send()
        return super().form_valid(form)
