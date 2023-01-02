import re

from django.db.models import Q
from haystack import indexes
from haystack.indexes import Indexable, NgramField, SearchIndex

from .models import Association

MAX_TERM_LENGTH_REGEX = re.compile(r"[^\s]{240,}")


class AssociationIndex(Indexable, SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    # the n-gram analyzer allows partial matches anywhere in the words
    # (EdgeNgramField would match only at the beginning)
    slug = NgramField(model_attr="slug")

    def prepare_text(self, obj):
        # xapian doesn’t support terms longer than 245 characters, but
        # our texts sometimes contain links and other stuff that may be
        # longer than that. replace everything that is longer than 240 chars
        return re.sub(MAX_TERM_LENGTH_REGEX, "", self.prepared_data["text"])

    def build_queryset(self, using=None, start_date=None, end_date=None):
        """allow filtering based start/end date for incremental updates

        We cannot use haystack's `get_updated_field` hook, since it expects only a single field
        name (while we need timestamps of content versions and contributions (comments)).
        """
        # retrieve the original queryset before applying time limits
        qs = super().build_queryset(using=using)
        if start_date:
            qs = qs.filter(
                Q(conversation__contributions__time_created__gte=start_date)
                | Q(content__versions__time_created__gte=start_date)
            )
        if end_date:
            qs = qs.filter(
                Q(conversation__contributions__time_created__lte=end_date)
                | Q(content__versions__time_created__lte=end_date)
            )
        return qs

    def get_model(self):
        return Association

    def index_queryset(self, using=None):
        return self.get_model().objects.exclude_deleted().filter(public=True)
