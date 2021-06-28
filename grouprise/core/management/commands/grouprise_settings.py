import argparse
import copy
import io
import json
import os
import sys

import ruamel.yaml

from django.core.management.base import BaseCommand, CommandError

from grouprise.settings_loader import load_settings_from_yaml_files


def _get_nested_dict_value(data, path, default=None):
    if not isinstance(data, dict):
        raise KeyError(f"Container is not a dictionary: {data}")
    elif len(path) == 0:
        return data
    elif len(path) == 1:
        data.setdefault(path[0], default)
        return data[path[0]]
    else:
        data.setdefault(path[0], {})
        return _get_nested_dict_value(data[path[0]], path[1:])


class Command(BaseCommand):
    """Management command for querying and manipulating settings.

    Changed settings are written to a configuration file.
    Beware, that the resolution order of configuration files may prevent a changed setting from
    becoming active (e.g. the setting in `/etc/grouprise/conf.d/800-local.yaml` is overrridden by
    the setting with the same name in `900-foo.yaml`).
    """

    help = "Query and manipulate grouprise settings"

    def add_arguments(self, parser):
        parser.add_argument("--format", choices=("json", "yaml"), default="yaml")
        parser.add_argument("--input", type=argparse.FileType("r"), default=sys.stdin)
        parser.add_argument(
            "--source-config",
            type=str,
            action="append",
            help=(
                "Location of configuration data (directory or filename). "
                "May be specified multiple times",
            ),
        )
        parser.add_argument(
            "--modifiable-config",
            type=str,
            default="/etc/grouprise/conf.d/800-local.yaml",
            help="Path of yaml file to be used for changing settings ('set')",
        )
        parser.add_argument("action", choices=("set", "get", "dump"))
        parser.add_argument("selector", nargs="?", type=str)

    @staticmethod
    def _get_parsed(raw, format_name):
        if format_name == "yaml":
            return ruamel.yaml.YAML().load(raw)
        elif format_name == "json":
            return json.loads(raw)
        else:
            raise ValueError(f"Unknown input format requested: {format_name}")

    @staticmethod
    def _get_formatted(data, format_name):
        if data is None:
            return ""
        elif format_name == "yaml":
            target = io.StringIO()
            ruamel.yaml.YAML().dump(data, target)
            lines = target.getvalue().splitlines()
            if lines[-1] == "...":
                lines.pop(-1)
            return os.linesep.join(lines)
        elif format_name == "json":
            return json.dumps(data)
        else:
            raise ValueError(f"Unknown output format requested: {format_name}")

    @staticmethod
    def _parse_selector(text):
        if not text:
            raise CommandError("Missing target variable name")
        tokens = [item.lower() for item in text.split(".")]
        if "" in tokens:
            raise CommandError(f"Invalid/empty field name in path: {text}")
        return tokens

    def handle(self, *args, **options):
        source_config_locations = options["source_config"]
        action = options["action"]
        if action == "dump":
            settings = load_settings_from_yaml_files(source_config_locations)
            self.stdout.write(self._get_formatted(settings, options["format"]))
        elif action == "get":
            tokens = self._parse_selector(options["selector"])
            settings = load_settings_from_yaml_files(source_config_locations)
            value = _get_nested_dict_value(settings, tokens)
            self.stdout.write(self._get_formatted(value, options["format"]))
        elif action == "set":
            raw = options["input"].read()
            input_data = self._get_parsed(raw, options["format"])
            tokens = self._parse_selector(options["selector"])
            filename = options["modifiable_config"]
            settings = load_settings_from_yaml_files([filename])
            original_settings = copy.copy(settings)
            parent = _get_nested_dict_value(settings, tokens[:-1], default={})
            parent[tokens[-1]] = input_data
            if settings != original_settings:
                config_dir = os.path.dirname(filename)
                if config_dir and not os.path.exists(config_dir):
                    os.makedirs(config_dir, exist_ok=True)
                with open(filename, "w") as output_file:
                    output_file.write(self._get_formatted(settings, "yaml"))
