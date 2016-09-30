from features.memberships import models as memberships


filters = {}


def register(filter_function):
    filters[filter_function.filter_id] = filter_function


def initial_author_no_member(association):
    return memberships.Membership.objects.filter(
            group=association.group,
            member=association.content.author
            ).exists()

initial_author_no_member.filter_id = 1
register(initial_author_no_member)
