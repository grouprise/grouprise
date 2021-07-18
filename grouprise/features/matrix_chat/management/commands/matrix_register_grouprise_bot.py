import atexit
import hashlib
import hmac
import os
import subprocess
import random
import string
import sys
import tempfile
import time
import urllib.error

import ruamel.yaml

from django.core.management.base import BaseCommand

from grouprise.features.matrix_chat.matrix_admin import MatrixAdmin
from grouprise.features.matrix_chat.settings import MATRIX_SETTINGS


DEFAULT_MATRIX_CONFIG_LOCATIONS = [
    "/etc/matrix-synapse/homeserver.yaml",
    "/etc/matrix-synapse/conf.d/",
]


def _get_random_string(length):
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def _restart_matrix_server(wait_seconds=None):
    try:
        subprocess.call(["service", "matrix-synapse", "restart"])
    except FileNotFoundError:
        subprocess.call(["systemctl", "restart", "matrix-synapse"])
    if wait_seconds:
        time.sleep(wait_seconds)


def _get_matrix_config_key(key, config_locations):
    get_config_key_args = ["/usr/share/matrix-synapse/get-config-key"]
    for location in config_locations:
        get_config_key_args.extend(["--config", location])
    get_config_key_args.append(key)
    try:
        token = subprocess.check_output(get_config_key_args, stderr=subprocess.PIPE)
    except OSError:
        return None
    except subprocess.CalledProcessError:
        # the key did not exist or any other failure
        return None
    if token:
        # remove newline (emitted by "get-config-key")
        token = token.strip()
    if token:
        return token.decode()
    else:
        return None


class Command(BaseCommand):
    help = "Register a grouprise bot with local admin privileges on the matrix server"

    def add_arguments(self, parser):
        parser.add_argument(
            "--bot-username",
            type=str,
            default=MATRIX_SETTINGS.BOT_USERNAME,
            help="local Matrix account username to be used for the grouprise bot",
        )
        parser.add_argument(
            "--matrix-api-url",
            type=str,
            default=MATRIX_SETTINGS.ADMIN_API_URL,
        )
        parser.add_argument(
            "--matrix-config-location",
            type=str,
            action="append",
            dest="matrix_config_locations",
            help=(
                "A matrix-synapse configuration file or directory. This argument may be specified "
                "multiple times."
            ),
        )
        parser.add_argument(
            "--modifiable-grouprise-config",
            type=str,
            default="/etc/grouprise/conf.d/200-matrix_chat.yaml",
            dest="modifiable_grouprise_config",
            help="Path of yaml file to be used for storing settings",
        )

    def request_admin_user_via_api(self, api, username, registration_token):
        """generate a user with admin privileges """
        # get a registration nonce
        register_api_path = "_synapse/admin/v1/register"
        nonce = api.request_get(register_api_path)["nonce"]
        password = "".join(random.choice(string.ascii_letters) for _ in range(64))
        mac = hmac.new(key=registration_token.encode("utf8"), digestmod=hashlib.sha1)
        mac.update(nonce.encode("utf8"))
        mac.update(b"\x00")
        mac.update(username.encode("utf8"))
        mac.update(b"\x00")
        mac.update(password.encode("utf8"))
        mac.update(b"\x00")
        mac.update(b"admin")
        response = api.request_post(
            register_api_path,
            {
                "nonce": nonce,
                "username": username,
                "password": password,
                "mac": mac.hexdigest(),
                "admin": True,
                "user_type": None,
            },
        )
        return response["access_token"]

    def register_admin_account(self, bot_username, matrix_api_url, config_locations):
        """register an admin account and return its access token

        This process is quite complicated, since we need to enable a registration token in advance
        and restart the matrix server.  This is not fun :(

        A proper solution is discussed in this issue:
            https://github.com/matrix-org/synapse/issues/5323
        """
        # retrieve an existing registration token (maybe one is configured)
        registration_token = _get_matrix_config_key(
            "registration_shared_secret", config_locations
        )
        if not registration_token:
            synapse_config_directories = [
                config_location
                for config_location in config_locations
                if os.path.isdir(config_location)
            ]
            if synapse_config_directories:
                config_directory = synapse_config_directories[0]
            else:
                config_directory = "/etc/matrix-synapse/conf.d"
            # generate a new configuration file with a registration token and restart the server
            handle, temp_registration_token_filename = tempfile.mkstemp(
                suffix=".yaml",
                prefix="zzz-grouprise-matrix-temporary-registration-key-",
                dir=config_directory,
            )

            def _cleanup_matrix_registration_configuration():
                try:
                    os.unlink(temp_registration_token_filename)
                except OSError:
                    pass
                _restart_matrix_server()

            atexit.register(_cleanup_matrix_registration_configuration)
            registration_token = _get_random_string(64)
            os.write(
                handle, b"registration_shared_secret: " + registration_token.encode()
            )
            os.close(handle)
            # sadly the matrix-synapse user needs read access to that file
            os.chmod(temp_registration_token_filename, 0o644)
            # wait for the restart of the matrix server
            _restart_matrix_server(10)
        else:
            temp_registration_token_filename = None
        # generate an admin token
        api = MatrixAdmin(None, matrix_api_url)
        try:
            bot_access_token = self.request_admin_user_via_api(
                api, bot_username, registration_token
            )
        except urllib.error.HTTPError as exc:
            error_message = "Failed to create grouprise bot account ('{}'). ".format(
                bot_username
            )
            if exc.code == 400:
                error_message += "Maybe it already exists?"
            else:
                error_message += "API response: {}".format(exc)
            self.stderr.write(self.style.ERROR(error_message))
            sys.exit(10)
        if temp_registration_token_filename:
            # remove the temporary configuration file and restart matrix again
            _cleanup_matrix_registration_configuration()
            atexit.unregister(_cleanup_matrix_registration_configuration)
        return bot_access_token

    def verify_configured_bot(self, matrix_api_url):
        api = MatrixAdmin(MATRIX_SETTINGS.BOT_ACCESS_TOKEN, matrix_api_url)
        try:
            user_id_for_token = api.request_get("_matrix/client/r0/account/whoami")[
                "user_id"
            ]
        except urllib.error.HTTPError as exc:
            if exc.code == 401:
                return False
        return user_id_for_token == "@{}:{}".format(
            MATRIX_SETTINGS.BOT_USERNAME, MATRIX_SETTINGS.DOMAIN
        )

    def handle(self, *args, **options):
        if (
            options["bot_username"] == MATRIX_SETTINGS.BOT_USERNAME
        ) and self.verify_configured_bot(options["matrix_api_url"]):
            self.stderr.write(
                self.style.NOTICE(
                    "The requested bot username ({}) is already configured properly.".format(
                        options["bot_username"]
                    )
                )
            )
        else:
            # we need to create a new user
            yaml = ruamel.yaml.YAML()
            grouprise_config_filename = options["modifiable_grouprise_config"]
            try:
                with open(grouprise_config_filename, "r") as config_file:
                    grouprise_settings = yaml.load(config_file)
            except PermissionError as exc:
                self.stderr.write(
                    f"Target configuration file ({grouprise_config_filename}) is not readable:"
                    f" {exc}"
                )
                sys.exit(1)
            except FileNotFoundError:
                grouprise_settings = None
            except IOError as exc:
                self.stderr.write(
                    f"Failed to read target configuration file ({grouprise_config_filename}):"
                    f" {exc}"
                )
                sys.exit(2)
            if not grouprise_settings:
                grouprise_settings = {}
            # test write permission in advance - otherwise we could loose the new bot token
            if not os.access(grouprise_config_filename, os.W_OK):
                self.stderr.write(
                    f"Target configuration file ({grouprise_config_filename}) is not writable"
                )
                sys.exit(3)
            config_locations = options["matrix_config_locations"]
            if not config_locations:
                config_locations = DEFAULT_MATRIX_CONFIG_LOCATIONS
            access_token = self.register_admin_account(
                options["bot_username"],
                options["matrix_api_url"],
                config_locations,
            )
            if "matrix_chat" not in grouprise_settings:
                grouprise_settings["matrix_chat"] = {}
            grouprise_settings["matrix_chat"]["admin_api_url"] = options["matrix_api_url"]
            grouprise_settings["matrix_chat"]["bot_access_token"] = access_token
            grouprise_settings["matrix_chat"]["bot_username"] = options["bot_username"]
            try:
                with open(grouprise_config_filename, "w") as config_file:
                    yaml.dump(grouprise_settings, config_file)
            except IOError as exc:
                self.stderr.write(
                    f"Failed to write new 'bot_access_token' ({access_token}) to target"
                    f" configuration file ({grouprise_config_filename}) {exc}"
                )
                sys.exit(4)
