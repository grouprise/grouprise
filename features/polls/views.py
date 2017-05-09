import itertools

import django

import core
import features.content.views
from . import forms, models


class Create(features.content.views.Create):
    template_name = 'polls/create.html'

    form_class = forms.Create


class Detail(features.content.views.DetailBase):
    template_name = 'polls/detail.html'

    def get_context_data(self, **kwargs):
        votes = models.Vote.objects.filter(option__poll=self.object.container).order_by('voter')
        votes = itertools.groupby(votes, lambda v: v.voter)
        kwargs['votes'] = {voter: [vv for vv in vvs] for voter, vvs in votes}
        kwargs['vote_form'] = forms.Vote()
        return super().get_context_data(**kwargs)


class Vote(core.views.PermissionMixin, django.views.generic.CreateView):
    permission_required = 'polls.vote'
    model = models.Vote
    form_class = forms.Vote

    def get_form_kwargs(self):
        self.association = self.get_association()
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = models.Vote(voter=self.request.user.gestalt)
        kwargs['options'] = self.association.container.options.all()
        return kwargs
    
    def get_success_url(self):
        return self.association.get_absolute_url()

    def get_association(self):
        return django.shortcuts.get_object_or_404(
                features.associations.models.Association,
                django.db.models.Q(group__slug=self.kwargs.get('entity_slug'))
                | django.db.models.Q(gestalt__user__username=self.kwargs.get('entity_slug')),
                slug=self.kwargs.get('association_slug'))
