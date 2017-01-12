from . import models
from content import models as content
from features.gestalten import models as gestalten


class Gestalt:
    @classmethod
    def score(cls, instance):
        if isinstance(instance, gestalten.Gestalt):
            s = models.Text.objects.filter(author=instance).count()
            s += content.Content.objects.filter(author=instance).count()
            s += content.Comment.objects.filter(author=instance).count()
            return s
        return 0
