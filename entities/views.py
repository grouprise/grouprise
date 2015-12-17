from django.views import generic

from . import models


class GroupDetailView(generic.DetailView):
    model = models.Group
