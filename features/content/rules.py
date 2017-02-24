from features.associations import models as associations
import rules


@rules.predicate
def can_view(user, association):
    return associations.Association.objects.can_view(user, container='content') \
            .filter(pk=association.pk).exists()


rules.add_perm(
        'content.view',
        can_view)
