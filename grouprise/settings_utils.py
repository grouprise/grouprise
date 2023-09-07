from typing import Callable, Tuple


class DelayedDictFieldResolver:
    """allow the delayed resolving of dictionary fields

    This may be used for certain Django settings, which depend on other settings, which may be
    overridden by our configuration files mechanism (e.g. `data_path`).
    Such references should be resolved *after* the configuration files are loaded.

    Initialize this class once and call the `get_resolver` method for each field to be resolved
    delayed.
    The result of this call needs to be stored in place of the setting to be resolved later.

    At some point (e.g. after all configuration files are processed), you need to call the
    `resolved_fields` method with the current data dictionary (for settings: `locals()`) as the
    only parameter.
    """

    def __init__(self):
        self._resolvables = []

    def get_resolver(self, dict_path: Tuple[str, ...], resolver: Callable):
        """this function is mainly used for registering a to-be-resolved callable"""
        self._resolvables.append(tuple(dict_path))
        # Simply return the resolver function.
        # We expect it to be stored in the dictionary.
        return resolver

    def resolve_fields(self, data_dict: dict):
        for dict_path in self._resolvables:
            try:
                parent, fieldname = self._get_nested_dict(data_dict, dict_path)
            except KeyError:
                # the path does not exist anymore - maybe the user overwrote it
                return
            else:
                if callable(parent[fieldname]):
                    parent[fieldname] = parent[fieldname](data_dict)

    @staticmethod
    def _get_nested_dict(data: dict, path: Tuple[str, ...]):
        """raise KeyError if the referenced field does not exist"""
        current_level = data
        # walk down the dictionary to the target element's parent
        for key in path[:-1]:
            current_level = current_level[key]
        # ensure that the final key exists
        current_level[path[-1]]
        return current_level, path[-1]


# this resolver must be a singleton (always import this instance - not the class above)
grouprise_field_resolver = DelayedDictFieldResolver()
