import re

import django.views.generic.edit
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.timezone import now

import core
from core.templatetags.core import ref
from features.associations.models import Association
from features.associations.views import AssociationMixin
from features.contributions.models import Contribution
from features.conversations.views import CreateGestaltConversation
from . import models


class Delete(AssociationMixin, core.views.PermissionMixin, django.views.generic.UpdateView):
    permission_required = 'contributions.delete'
    queryset = models.Contribution.objects_with_internal
    fields = []
    template_name = 'contributions/delete.html'

    def get_form_kwargs(self):
        self.association = self.get_association()
        kwargs = super().get_form_kwargs()
        kwargs['instance'].deleted = now()
        return kwargs

    def get_success_url(self):
        return self.association.get_absolute_url()


class ReplyToAuthor(CreateGestaltConversation):
    permission_required = 'contributions.reply_to_author'

    def get_initial(self):
        subject = 'Re: {}'.format(self.contribution.container.subject)
        if self.association.container.is_conversation:
            permalink_url = reverse('conversation', args=[self.association.pk])
        else:
            permalink_url = reverse('content-permalink', args=[self.association.pk])
        text = '{}\n — [{}]({}#{})'.format(
                self.contribution.contribution.text, self.contribution.author,
                permalink_url, ref(self.contribution))
        text = re.sub('^', '> ', text, flags=re.MULTILINE)
        return {'subject': subject, 'text': text}

    def get_permission_object(self):
        self.association = get_object_or_404(
                Association, pk=self.kwargs.get('association_pk'))
        self.contribution = get_object_or_404(
                Contribution.objects_with_internal, pk=self.kwargs.get('contribution_pk'))
        self.entity = self.contribution.author
        return self.contribution
