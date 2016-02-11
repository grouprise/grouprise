from django.db import models


class GroupContentQuerySet(models.QuerySet):
    def galleries(self):
        return self.exclude(content__gallery=None)

    def pinned(self):
        return self.filter(pinned=True)

    def unpinned(self):
        return self.filter(pinned=False)

    def without_galleries(self):
        return self.filter(content__gallery=None)
