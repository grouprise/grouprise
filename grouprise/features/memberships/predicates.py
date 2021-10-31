import rules

from . import models


@rules.predicate
def applicant_is_member(user, application):
    return is_member_of(application.contribution.author.user, application.group)


@rules.predicate
def is_member(user, membership):
    if membership:
        return membership.member == user.gestalt
    return False


@rules.predicate
def is_member_of(user, group):
    if group:
        try:
            return models.Membership.objects.filter(
                group=group, member=user.gestalt
            ).exists()
        except AttributeError:
            return None


@rules.predicate
def is_member_of_application_group(user, application):
    return is_member_of(user, application.group)
