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

from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
from django.views import generic
from core.views import base
from features.groups import models as group_models
from content import models as content_models
from .models import Tagged, Tag


def get_tag_context(tag, user, page_number):
    groups = group_models.Group.objects.filter(
        Tagged.get_tagged_query(tag, group_models.Group)
    )
    content = content_models.Content.objects.permitted(user).filter(
        Tagged.get_tagged_query(tag, content_models.Content)
    )
    group_ids = groups.values_list('id')
    events = content_models.Event.objects.permitted(user).filter(
        Tagged.get_tagged_query(tag, content_models.Event) | Q(groupcontent__group__in=group_ids)
    )
    paginator = Paginator(content, 10)
    try:
        page = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page = paginator.page(1)

    return {'groups': groups, 'events': events, 'paginator': paginator, 'content_page': page}


class TagPage(base.PermissionMixin, generic.DetailView):
    permission_required = 'tags.view'
    model = Tag
    template_name = 'tags/tag.html'
    sidebar = ()

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except Http404:
            slug = self.kwargs.get(self.slug_url_kwarg)
            tag = Tag()
            tag.name = slug
            return tag

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page', 1)
        user = self.request.user

        if context['object'].pk is not None:
            context['no_data'] = False
            context.update(get_tag_context(self.object, user, page))
        else:
            context['no_data'] = True
        return context
