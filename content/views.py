from django.views import generic

from . import models


class ContentDetailView(generic.DetailView):
    model = models.Content
