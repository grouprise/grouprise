import json
import os


def get_version_tuple():
    package_file = os.path.join(os.path.abspath(
        os.path.dirname(__file__)), os.path.pardir, "package.json")
    version_string = json.load(open(package_file, "r"))["version"]
    return tuple([int(v) for v in version_string.split(".")])


def get_version():
    return "%d.%d.%d" % get_version_tuple()


def _get_next_version_by_index(update_position_index):
    """ calculate the next version string by incrementing the version number at the given position
    """
    current_version = get_version_tuple()
    next_version = []
    for index in range(3):
        if index < update_position_index:
            next_version.append(current_version[index])
        elif index == update_position_index:
            next_version.append(current_version[index] + 1)
        elif index > update_position_index:
            next_version.append(0)
    return "%d.%d.%d" % tuple(next_version)


def get_next_breaking_version():
    return _get_next_version_by_index(0)


def get_next_feature_version():
    return _get_next_version_by_index(1)


def get_next_patch_version():
    return _get_next_version_by_index(2)
