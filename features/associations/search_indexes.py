from haystack import indexes
from haystack.indexes import Indexable, SearchIndex

from .models import Association


class AssociationIndex(Indexable, SearchIndex):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Association

    def index_queryset(self, using=None):
        return self.get_model().objects.exclude_deleted().filter(public=True)
