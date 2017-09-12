import django

import core
import features
from . import models


class Create(
        core.views.PermissionMixin, features.associations.views.AssociationMixin,
        django.views.generic.CreateView):
    permission_required = 'board.create'
    model = models.Note

    def get_permission_object(self):
        self.association = self.get_association()
