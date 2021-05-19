import asyncio
import sys

from django.core.management.base import BaseCommand

from grouprise.features.groups.models import Group
from grouprise.features.matrix_chat.matrix_bot import MatrixBot


class Command(BaseCommand):
    args = ""
    help = "Synchronize rooms and other state from grouprise to matrix"

    def add_arguments(self, parser):
        parser.add_argument("action", choices=("create-rooms", "invite-room-members"))

    def handle(self, *args, **options):
        action = options["action"]
        if action == "create-rooms":

            async def create_group_rooms(groups):
                async with MatrixBot() as bot:
                    for group in groups:
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
        else:
            self.stderr.write(
                self.style.ERROR("Invalid action requested: {}".format(action))
            )
            sys.exit(1)
