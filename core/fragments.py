fragments = {}
groups = {}


def register(key, fragment):
    fragments[key] = fragment


def always():
    return True


def insert(key, group_name, predicate=always, after=[], before=[]):
    group = groups.get(group_name, [])
    min_index = 0
    for item in after:
        try:
            min_index = max(min_index, group.index(item)+1)
        except ValueError:
            pass
    max_index = len(group)
    for item in before:
        try:
            max_index = min(max_index, group.index(item))
        except ValueError:
            pass
    if min_index <= max_index:
        group.insert(max_index, key)
        groups[group_name] = group


def register2(fragment, group, **kwargs):
    key = '{}-{}'.format(group, fragment)
    register(key, fragment)
    insert(key, group, **kwargs)
