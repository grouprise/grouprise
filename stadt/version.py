from stadt import VERSION


def get_version_tuple():
    return tuple([int(v) for v in VERSION.split(".")])


def get_version():
    return VERSION
