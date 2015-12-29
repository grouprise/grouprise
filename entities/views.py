from django.views import generic

from . import models


class GestaltDetailView(generic.DetailView):
    model = models.Gestalt


class GroupDetailView(generic.DetailView):
    model = models.Group
