import re

import django
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView
from haystack.inputs import AutoQuery
from haystack.query import EmptySearchQuerySet, SearchQuerySet

import grouprise.core
from grouprise.core.views import PermissionMixin
from grouprise.features import gestalten, groups
from grouprise.features.content import views as content
from grouprise.features.conversations.views import CreateGroupConversation
from grouprise.features.groups.models import Group


class Entity(grouprise.core.views.PermissionMixin, django.views.generic.View):
    def get(self, request, *args, **kwargs):
        context = self.view.get_context_data(object=self.view.object)
        return self.view.render_to_response(context)

    def get_object(self):
        slug = self.kwargs.get("entity_slug")
        try:
            return Group.objects.get(slug=slug)
        except Group.DoesNotExist:
            return get_object_or_404(gestalten.models.Gestalt, user__username=slug)

    def get_view(self):
        # choose view based on entity type
        entity = self.get_object()
        if entity.is_group:
            view = groups.views.Detail()
        else:
            view = gestalten.views.Detail()

        # set view attributes
        view.object = entity
        view.object_list = None
        view.kwargs = self.kwargs
        view.request = self.request

        return view

    def has_permission(self):
        self.view = self.get_view()
        return self.view.has_permission()


class Help(CreateGroupConversation):
    template_name = "stadt/help.html"

    def get_context_data(self, **kwargs):
        intro = (
            self.entity.associations.ordered_user_content(self.request.user)
            .filter(pinned=True)
            .order_by("time_created")
        )
        intro_gallery = intro.filter_galleries().filter(public=True).first()
        if intro_gallery:
            intro = intro.exclude(pk=intro_gallery.pk)
        about_text = intro.first()
        tools_text = (
            self.entity.associations.ordered_user_content(self.request.user)
            .filter(slug="tools")
            .first()
        )
        if about_text:
            kwargs["about_text"] = about_text
            if tools_text and tools_text != about_text:
                kwargs["tools_text"] = tools_text
        return super().get_context_data(**kwargs)

    def get_permission_object(self):
        self.entity = Group.objects.operator_group()
        return self.entity


class Index(content.List):
    template_name = "stadt/index.html"

    def get_context_data(self, **kwargs):
        kwargs["feed_url"] = self.request.build_absolute_uri(reverse("feed"))
        return super().get_context_data(**kwargs)


class Privacy(django.views.generic.TemplateView):
    permission_required = "stadt.view_privacy"
    template_name = "stadt/privacy.html"
    title = "Datenschutz"


class Search(PermissionMixin, ListView):
    permission_required = "stadt.search"
    paginate_by = 12
    template_name = "stadt/search.html"

    def get_queryset(self):
        self.query_string = re.sub(r"[^\w ]", "", self.request.GET.get("q", ""))
        if self.query_string:
            return SearchQuerySet().filter(content=AutoQuery(self.query_string))
        else:
            return EmptySearchQuerySet()
