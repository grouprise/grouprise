import asyncio
import datetime
import io
import sys

import ruamel.yaml

from django.core.management.base import BaseCommand

from grouprise.core.settings import get_grouprise_baseurl, get_grouprise_site
from grouprise.features.groups.models import Group
from grouprise.features.matrix_chat.matrix_bot import MatrixBot
from grouprise.features.matrix_chat.models import MatrixChatGroupRoom
from grouprise.features.matrix_chat.settings import (
    get_or_create_oidc_client_application,
)


class Command(BaseCommand):
    args = ""
    help = "Synchronize rooms and other state from grouprise to matrix"

    def add_arguments(self, parser):
        parser.add_argument(
            "--group",
            help="Limit the action to a specific group (identified by its slug)",
        )
        parser.add_argument(
            "action",
            choices=(
                "configure-rooms",
                "update-statistics",
                "invite-room-members",
                "print-statistics",
                "print-synapse-configuration",
            ),
        )

    def handle(self, *args, **options):
        action = options["action"]
        if action == "configure-rooms":

            async def create_group_rooms(groups):
                async with MatrixBot() as bot:
                    for group in groups:
                        if options["group"] and (group.slug != options["group"]):
                            continue
                        async for updated_room in bot.synchronize_rooms_of_group(group):
                            self.stdout.write(
                                self.style.NOTICE(
                                    f"Created or updated room '{updated_room}'"
                                )
                            )

            asyncio.run(create_group_rooms(list(Group.objects.all())))
        elif action == "invite-room-members":

            async def invite_to_group_rooms(groups):
                async with MatrixBot() as bot:
                    for group in groups:
                        if options["group"] and (group.slug != options["group"]):
                            continue
                        async for (
                            room,
                            gestalt,
                        ) in bot.send_invitations_to_group_members(group):
                            self.stdout.write(
                                self.style.NOTICE(
                                    f"Invited '{gestalt}' to room '{room}'"
                                )
                            )

            asyncio.run(invite_to_group_rooms(list(Group.objects.all())))
        elif action == "print-synapse-configuration":
            site = get_grouprise_site()
            matrix_chat_app = get_or_create_oidc_client_application()
            settings = {
                "enable_registration": False,
                "password_config": {"enabled": False},
                # synapse refuses to enable OIDC without a configured "public_baseurl"
                "public_baseurl": get_grouprise_baseurl() + "/",
                # The web client location can be used for discovering web clients of external
                # homeservers: https://example.org/_matrix/client
                "web_client_location": get_grouprise_baseurl() + "/stadt/chat/",
                "oidc_providers": [
                    {
                        "idp_id": site.domain,
                        "idp_name": site.name,
                        "issuer": get_grouprise_baseurl() + "/stadt/oauth/",
                        "client_id": matrix_chat_app.client_id,
                        "client_secret": matrix_chat_app.client_secret,
                        "client_auth_method": "client_secret_post",
                        "discover": True,
                        "scopes": ["openid"],
                        "skip_verification": True,
                        "user_mapping_provider": {
                            "config": {
                                "subject_claim": "id",
                                "localpart_template": "{{ user.id }}",
                                "display_name_template": "{{ user.display_name }}",
                                "email_template": "{{ user.email }}",
                            },
                        },
                    }
                ],
            }
            target = io.StringIO()
            ruamel.yaml.YAML().dump(settings, target)
            print(f"# generated by: grouprisectl matrix_chat_manage {action}")
            print()
            print(target.getvalue())
        elif action == "print-statistics":
            for room in MatrixChatGroupRoom.objects.order_by("group__slug"):
                stats = room.get_statistics()
                members_count = stats.get("members_count", 0)
                try:
                    timestamp = stats["last_message_timestamp"]
                except KeyError:
                    timestamp_text = ""
                else:
                    timestamp_text = datetime.datetime.fromtimestamp(
                        timestamp
                    ).strftime("%Y-%m-%d")
                room_text = "{} ({})".format(
                    room.group.slug, "private" if room.is_private else "public"
                )
                self.stdout.write(
                    f"{room_text:50s} {members_count:3d} {timestamp_text}"
                )
        elif action == "update-statistics":

            async def update():
                async with MatrixBot() as bot:
                    await bot.update_statistics()

            asyncio.run(update())
        else:
            self.stderr.write(
                self.style.ERROR("Invalid action requested: {}".format(action))
            )
            sys.exit(1)
