from . import models
import rules


@rules.predicate
def is_permitted(user, instance):
    if instance:
        if hasattr(instance, 'content'):
            return models.Content.objects.permitted(user).filter(pk=instance.content.pk).exists()
        else:
            return models.Content.objects.permitted(user).filter(pk=instance.pk).exists()
    return False


@rules.predicate
def is_author(user, instance):
    if hasattr(instance, 'author'):
        return instance.author == user.gestalt
    else:
        return instance.content.author == user.gestalt


@rules.predicate
def is_group_content(user, content):
    return content.groups.exists()


@rules.predicate
def is_public(user, content):
    return content.public


@rules.predicate
def is_recipient(user, content):
    for gestalt in content.gestalten.all():
        if user.gestalt == gestalt:
            return True
    return False
