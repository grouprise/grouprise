import haystack
from haystack.indexes import Indexable, NgramField, SearchIndex

from .models import Group


class GroupIndex(Indexable, SearchIndex):
    text = haystack.indexes.CharField(document=True, use_template=True)
    # the n-gram analyzer allows partial matches anywhere in the words
    # (EdgeNgramField would match only at the beginning)
    address = NgramField(model_attr="address")
    description = NgramField(model_attr="description")
    name = NgramField(model_attr="name")
    slug = NgramField(model_attr="slug")

    def get_model(self):
        return Group

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
