from os import environ

try:
    from stadt.settings.local import *  # noqa: 401
except ImportError:
    from stadt.settings.default import *  # noqa: 401

try:
    preset = environ['STADTGESTALTEN_PRESET'].lower()

    if preset == 'development':
        from stadt.settings.development import *  # noqa: 401
    elif preset == 'packaging':
        from stadt.settings.packaging import *  # noqa: 401
    elif preset == 'test':
        from stadt.settings.test import *  # noqa: 401
    else:
        raise ValueError('unknown preset "%s"' % preset)
except KeyError:
    pass
