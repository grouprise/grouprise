from django.views import generic

from . import models


class ContentDetailView(generic.DetailView):
    model = models.Content


class ContentListView(generic.ListView):
    model = models.Content
