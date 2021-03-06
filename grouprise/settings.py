import os
import sys

LEGACY_CONFIG_FILENAME = "/etc/grouprise/settings.py"

if os.path.exists(LEGACY_CONFIG_FILENAME):
    # temporary support for the old configuration mechanism
    print(
        f"WARNING: the deprecated grouprise configuration file {LEGACY_CONFIG_FILENAME} exists. "
        "It will be used for now, but you should migrate to the new configuration format soon. "
        "See https://docs.grouprise.org/releases/4.0.html for details.",
        file=sys.stderr,
    )
    sys.path.insert(0, os.path.dirname(LEGACY_CONFIG_FILENAME))
    from settings import *  # noqa: F401 F403

    sys.path.pop(0)
else:
    # use the new configuration format
    from grouprise.common_settings import *  # noqa: F401 F403
    from grouprise.settings_loader import import_settings_from_yaml

    import_settings_from_yaml(locals())
