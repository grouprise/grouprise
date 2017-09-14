import django

import core
import features
from . import forms


class Create(
        core.views.PermissionMixin, features.associations.views.AssociationMixin,
        django.views.generic.CreateView):
    permission_required = 'board.create'
    form_class = forms.Create
    template_name = 'board/create.html'

    def get_permission_object(self):
        self.association = self.get_association()
        return self.association
