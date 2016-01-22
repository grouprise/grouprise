from django.db import models


class GroupContentQuerySet(models.QuerySet):
    def galleries(self):
        return self.exclude(content__gallery=None)

    def pinned(self):
        return self.filter(pinned=True)

    def pinned_without_head_gallery(self):
        pinned = self.pinned()
        gallery = pinned.galleries().first()
        if gallery:
            return pinned.exclude(pk=gallery.pk)
        else:
            return pinned

    def unpinned(self):
        return self.filter(pinned=False)
