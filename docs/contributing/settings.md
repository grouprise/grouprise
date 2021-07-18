# Managing grouprise settings

Grouprise is configured via [yaml-based configuration files](/administration/configuration/files).

The content of these files is parsed and transferred into Django settings.
This simplifies the access to settings from within the Django-based application code.

Within the *grouprise* code settings are usually accessed like this:
```python
from grouprise.core.settings import CORE_SETTINGS

print(CORE_SETTINGS.BACKUP_PATH)
```

Most settings are available in `CORE_SETTINGS`.
In addition there are also app-specific dictionaries (e.g. see `grouprise/features/matrix_chat/settings.py`).

In order to change existing settings or add new ones, the following steps are recommended:

1. configure the setting processing in `grouprise/settings_loader.py`
1. expose the setting in the corresponding grouprise app
    * e.g. `grouprise/core/settings.py` or `grouprise/features/*/settings.py`
1. add tests for configuration handling in `grouprise/tests.py`
    * only relevant for non-trivial settings
1. document the setting in `docs/administration/configuration/options.md`
1. mention the setting in the upcoming release notes (below `docs/releases/`)
