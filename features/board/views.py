import django

import core
import features
from . import forms, models


class Create(
        core.views.PermissionMixin, features.associations.views.AssociationMixin,
        django.contrib.messages.views.SuccessMessageMixin, django.views.generic.CreateView):
    permission_required = 'board.create'
    form_class = forms.Create
    template_name = 'board/create.html'
    success_message = 'Notiz wurde am "Schwarzen Brett" auf der Startseite angeheftet.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = models.Note(related_to=self.association)
        if self.request.user.is_authenticated():
            kwargs['instance'].gestalt_created = self.request.user.gestalt
        return kwargs

    def get_permission_object(self):
        self.association = self.get_association()
        return self.association

    def get_success_url(self):
        return self.association.get_absolute_url()
