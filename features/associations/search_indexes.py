import re
from haystack import indexes
from haystack.indexes import Indexable, SearchIndex

from .models import Association

MAX_TERM_LENGTH_REGEX = re.compile(r'[^\s]{240,}')


class AssociationIndex(Indexable, SearchIndex):
    text = indexes.CharField(document=True, use_template=True)

    def prepare_text(self, obj):
        # xapian doesn’t support terms longer than 245 characters, but
        # our texts sometimes contain links and other stuff that may be
        # longer than that. replace everything that is longer than 240 chars
        return re.sub(MAX_TERM_LENGTH_REGEX, '', self.prepared_data['text'])

    def get_model(self):
        return Association

    def index_queryset(self, using=None):
        return self.get_model().objects.exclude_deleted().filter(public=True)
