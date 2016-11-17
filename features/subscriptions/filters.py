filters = {}


def register(filter_function):
    filters[filter_function.filter_id] = filter_function


def initial_author_no_member(association):
    return association.is_external()


initial_author_no_member.filter_id = 1
register(initial_author_no_member)


def all_content(association):
    return True


all_content.filter_id = 2
register(all_content)
