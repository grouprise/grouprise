from django.db import models


class GroupContentQuerySet(models.QuerySet):
    def pinned(self):
        return self.filter(pinned=True)

    def unpinned(self):
        return self.filter(pinned=False)
