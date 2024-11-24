"""Inject the environment variable GDAL_VERSION_SPECIFICATION into all hatch environments."""

import os
import subprocess

from hatch.env.collectors.plugin.interface import EnvironmentCollectorInterface


def _get_gdal_specification_for_available_version() -> str | None:
    """determine the local version of gdal and return a suitable version specification

    An empty string is returned, if gdal is not installed.
    """
    try:
        get_config_call = subprocess.run(
            ["gdal-config", "--version"], capture_output=True, check=True
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        # "any" version is fine
        return ""
    else:
        version = get_config_call.stdout.decode().strip()
        return f"=={version}"


class GroupriseEnvironmentCollector(EnvironmentCollectorInterface):
    PLUGIN_NAME = "custom"

    ENVIRONMENT_OVERRIDES = {
        "GDAL_VERSION_SPECIFICATION": _get_gdal_specification_for_available_version(),
    }

    def get_initial_config(self) -> dict[str, dict]:
        # extra: set the real environment of the current process
        for key, value in self.ENVIRONMENT_OVERRIDES.items():
            os.environ.setdefault(key, value)
        return {}

    def finalize_config(self, config: dict[str, dict]) -> None:
        for env_name, env_entry in config.items():
            env_dict = env_entry.setdefault("env-vars", {})
            for key, value in self.ENVIRONMENT_OVERRIDES.items():
                env_dict.setdefault(key, value)
        return config
