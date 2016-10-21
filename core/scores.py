def get_score_processors():



def update(model):
    for instance in model._default_manager.all():
        instance.score = 0
        for p in get_score_processors():
            instance.score += p(instance)
        instance.save()
