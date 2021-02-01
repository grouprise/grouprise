import haystack
from haystack.indexes import Indexable, SearchIndex

from .models import Group


class GroupIndex(Indexable, SearchIndex):
    text = haystack.indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Group

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
