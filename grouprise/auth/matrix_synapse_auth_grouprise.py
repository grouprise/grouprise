"""
Authentication module for using a grouprise instance as the authentication handler for
a matrix-synapse server.

Please note: the grouprise instance must run on the same host as the matrix-synapse server.
This authentication module uses the Django mechanism for loading the grouprise configuration.
Thus at least the full set of dependencies for grouprise as well as the grouprise configuration
file must be available.
Grouprise does not offer any remote authentication mechanism, thus there is no way to work around
this limitation.

Configuration:
* grouprise and Django (as well as all dependencies) need to be available within matrix-synapse,
  thus the following environment setting (in /etc/default/matrix-synapse) is necessary:
    PYTHONPATH=/usr/share/grouprise/python-lib:/usr/share/grouprise/dependencies
* specify the authentication backend (somewhere below /etc/matrix-synapse/conf.d/):
    password_providers:
    - module: "grouprise.auth.matrix_synapse_auth_grouprise.GroupriseAuthProvider"
      config:
        enabled: true
        settings_filename: /etc/grouprise/settings.py
* allow the matrix user to read the grouprise configuration:
    chmod 644 /etc/grouprise/settings.py
"""

import importlib
import logging
import types

import django
import django.conf
from django.contrib.auth import authenticate


logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """ Any kind of problem related to loading and using the configuration """


def _load_grouprise_configuration(filename):
    spec = importlib.util.spec_from_file_location("grouprise_settings", filename)
    grouprise_settings = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(grouprise_settings)
    except ImportError as exc:
        raise ConfigurationError(
            "Failed to load module for grouprise authentication: {}".format(exc)
        )
    settings_dict = {}
    for key in dir(grouprise_settings):
        value = getattr(grouprise_settings, key)
        if key.startswith("_"):
            continue
        if isinstance(value, types.ModuleType):
            continue
        settings_dict[key] = value
    django.conf.settings.configure(**settings_dict)
    django.setup()
    return grouprise_settings


class GroupriseAuthProvider:
    def __init__(self, config, account_handler):
        self.account_handler = account_handler

        if not hasattr(config, "settings_filename"):
            raise ConfigurationError(
                "Grouprise authentication requires 'settings_filename'"
            )

        settings_filename = config.settings_filename

        self.grouprise_settings = _load_grouprise_configuration(settings_filename)

    @staticmethod
    def parse_config(config):
        class _Config:
            pass

        result = _Config()
        result.settings_filename = config.get(
            "settings_filename", "/etc/grouprise.settings.py"
        )
        return result

    def get_supported_login_types(self):
        return {"m.login.password": ("password",)}

    def _authenticate_email(self, email_address, password):
        # this import may not happen before the django configuration
        from grouprise.features.gestalten.models import Gestalt
        try:
            email_user = Gestalt.objects.get_by_email(email_address).user
        except Gestalt.DoesNotExist:
            return None
        else:
            return authenticate(username=email_user.username, password=password)

    async def check_auth(self, username, login_type, login_dict):
        """Attempt to authenticate a user against a grouprise instance
        and register an account if none exists.

        Returns:
            Canonical user ID if authentication against grouprise was successful
        """

        # tolerate a matrix ID and extract its local part
        if username.startswith("@") and ":" in username:
            # username is given as a matrix ID (@foo:bar.com)
            username = username.split(":", 1)[0][1:]
        password = login_dict["password"]

        # try to authenticate the user by its username
        user = authenticate(username=username, password=password)
        if (user is None) and ("@" in username):
            # try to authenticate the user belonging to this email address
            user = self._authenticate_email(username, password)
        if user is None:
            return False
        else:
            return await self.register_user_if_not_exists(user)

    async def check_3pid_auth(self, medium, address, password):
        if medium != "email":
            return False
        user = self._authenticate_email(address, password)
        if user is None:
            return False
        else:
            return await self.register_user_if_not_exists(user)

    async def register_user_if_not_exists(self, grouprise_user):
        """Register a Synapse user, first checking if they exist.

        Args:
            localpart (str): Localpart of the user to register on this homeserver.
            name (str): Full name of the user.
            email_address (str): Email address of the user.

        Returns:
            user_id (str): User ID of the newly registered user.
        """
        localpart = grouprise_user.username
        name = grouprise_user.gestalt.name
        email_address = grouprise_user.email
        # The grouprise user name is used as the local part of the Matrix ID.
        if await self.account_handler.check_user_exists(localpart):
            return localpart
        # Get full user id from localpart
        user_id = self.account_handler.get_qualified_user_id(localpart)
        if await self.account_handler.check_user_exists(user_id):
            # exists, authentication complete
            return user_id
        else:
            # create the matrix user
            emails = [email_address] if email_address is not None else []
            user_id, access_token = await self.account_handler.register(
                localpart=localpart,
                displayname=name,
                emails=emails,
            )
            logger.info("Registration based on Grouprise was successful: %s", user_id)
            return user_id
