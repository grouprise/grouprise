import django

import grouprise.core
import grouprise.features
from . import forms, models


class Create(grouprise.features.content.views.Create):
    template_name = "polls/create.html"

    form_class = forms.Create


class Detail(grouprise.features.content.views.DetailBase):
    template_name = "polls/detail.html"


class Vote(grouprise.core.views.PermissionMixin, django.views.generic.CreateView):
    permission_required = "polls.vote"
    model = models.SimpleVote
    form_class = forms.Vote

    def form_invalid(self, form):
        view = Detail(kwargs=self.kwargs, request=self.request)
        view.vote_form = form
        return view.get(self.request)

    def get(self, *args, **kwargs):
        return django.http.HttpResponseRedirect(
            django.urls.reverse(
                "content",
                args=[
                    self.kwargs.get("entity_slug"),
                    self.kwargs.get("association_slug"),
                ],
            )
        )

    def get_association(self):
        return django.shortcuts.get_object_or_404(
            grouprise.features.associations.models.Association,
            django.db.models.Q(group__slug=self.kwargs.get("entity_slug"))
            | django.db.models.Q(
                gestalt__user__username=self.kwargs.get("entity_slug")
            ),
            slug=self.kwargs.get("association_slug"),
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            kwargs["instance"] = models.SimpleVote(voter=self.request.user.gestalt)
        kwargs["poll"] = self.association.container.poll
        return kwargs

    def get_permission_object(self):
        self.association = self.get_association()
        return self.association

    def get_success_url(self):
        return self.association.get_absolute_url()
