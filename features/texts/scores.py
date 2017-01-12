from features.gestalten import models as gestalten


class Gestalt:
    @classmethod
    def score(cls, instance):
        if isinstance(instance, gestalten.Gestalt):
            s = 0
            return s
        return 0
