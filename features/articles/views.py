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

import django.db.models
from django.views import generic

from core.views import base
import features.content.views
from features.associations import models as associations
from features.content import models as content


class List(base.PermissionMixin, generic.ListView):
    permission_required = 'articles.view_list'
    model = associations.Association
    template_name = 'articles/list.html'
    paginate_by = 10

    def get_content(self):
        return associations.Association.objects.can_view(self.request.user)

    def get_queryset(self):
        return super().get_queryset().filter(
                container_type=content.Content.content_type, content__time__isnull=True,
                ).can_view(self.request.user).annotate(time_created=django.db.models.Min(
                    'content__versions__time_created')).order_by('-time_created')


class Create(features.content.views.Create):
    template_name = 'articles/create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['with_time'] = False
        return kwargs
