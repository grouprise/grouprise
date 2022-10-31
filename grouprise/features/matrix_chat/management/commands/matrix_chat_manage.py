import datetime
import io
import sys

from asgiref.sync import async_to_sync, sync_to_async
import ruamel.yaml
from django.core.management.base import BaseCommand

from grouprise.core.settings import get_grouprise_baseurl, get_grouprise_site
from grouprise.features.groups.models import Group
from grouprise.features.matrix_chat.matrix_bot import ChatBot
from grouprise.features.matrix_chat.models import MatrixChatGroupRoom
from grouprise.features.matrix_chat.settings import (
    get_or_create_oidc_client_application,
)


class Command(BaseCommand):
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

    @async_to_sync
    async def handle(self, *args, **options):
        def get_all_groups():
            return list(Group.objects.all())

        action = options["action"]
        if action == "configure-rooms":
            groups = await sync_to_async(get_all_groups)()
            async with ChatBot() as bot:
                for group in groups:
                    if options["group"] and (group.slug != options["group"]):
                        continue
                    async for updated_room in bot.synchronize_rooms_of_group(group):
                        updated_room_label = await sync_to_async(str)(updated_room)
                        self.stdout.write(
                            self.style.NOTICE(
                                f"Created or updated room '{updated_room_label}'"
                            )
                        )
        elif action == "invite-room-members":
            groups = await sync_to_async(get_all_groups)()
            async with ChatBot() as bot:
                for group in groups:
                    if options["group"] and (group.slug != options["group"]):
                        continue
                    async for (
                        room,
                        gestalt,
                    ) in bot.send_invitations_to_group_members(group):
                        gestalt_label = await sync_to_async(str)(gestalt)
                        room_label = await sync_to_async(str)(room)
                        self.stdout.write(
                            self.style.NOTICE(
                                f"Invited '{gestalt_label}' to room '{room_label}'"
                            )
                        )
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
                        "scopes": ["email", "openid", "profile"],
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
            async with ChatBot() as bot:
                await bot.update_statistics()
        else:
            self.stderr.write(
                self.style.ERROR("Invalid action requested: {}".format(action))
            )
            sys.exit(1)
