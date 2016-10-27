from django.conf import settings
from django.utils import module_loading


def get_score_processors():
    return [module_loading.import_string(s) for s in settings.SCORE_PROCESSORS]


def update(model):
    for instance in model._default_manager.all():
        instance.score = 0
        for p in get_score_processors():
            instance.score += p(instance)
        instance.save()
