import difflib
import os

from grouprise.features.gestalten.models import Gestalt

from kien import create_commander, var, CommandResult
import kien.command.help as help_command
from kien.utils import strip_tags
import kien.error


commander = create_commander("grouprise-commander")


class MultilineResult(CommandResult):
    def __init__(self, response_lines, *args, **kwargs):
        super().__init__(os.linesep.join(response_lines), *args, **kwargs)


def get_unknown_username_response(username, max_alternative_count=10):
    all_usernames = (
        item.user.username for item in Gestalt.objects.only("user__username")
    )
    yield CommandResult(f"Unknown username: {username}", success=False)
    closest_matches = difflib.get_close_matches(
        username, all_usernames, max_alternative_count
    )
    if closest_matches:
        yield CommandResult("Maybe you meant one of the following?", success=False)
        for item in closest_matches:
            yield CommandResult("  " + item, success=False)


@commander("user", is_abstract=True)
def user_commands():
    pass


@commander("list", "unused", var("limit", is_optional=True), parent=user_commands)
def user_list_unused(limit: int = 5):
    result = []
    # TODO: verify the following queryset
    for gestalt in Gestalt.objects.filter(
        associations=None,
        contributions=None,
        groups=None,
        images=None,
        memberships=None,
        subscriptions=None,
        user__last_login=None,
        versions=None,
    ).order_by("activity_bookmark_time")[:limit]:
        if not gestalt.user.has_usable_password():
            yield CommandResult(f"{gestalt.user.username} ({gestalt.user.date_joined})")


@commander("show", var("username"), parent=user_commands)
def show_user(username):
    try:
        gestalt = Gestalt.objects.get(user__username=username)
    except Gestalt.DoesNotExist:
        yield from get_unknown_username_response(username)
    else:
        yield CommandResult(f"Username: {gestalt.user.username}")
        yield CommandResult(f"Email: {gestalt.user.email}")
        yield CommandResult(f"Contributions: {gestalt.contributions.count()}")
        yield CommandResult(f"Group memberships: {gestalt.memberships.count()}")
        latest_contribution = gestalt.contributions.order_by("time_created").last()
        timestamp = latest_contribution.time_created if latest_contribution else None
        yield CommandResult(f"Latest contribution: {timestamp}")


@commander("remove", var("username"), parent=user_commands)
def remove_user(username):
    try:
        gestalt = Gestalt.objects.get(user__username=username)
    except Gestalt.DoesNotExist:
        yield from get_unknown_username_response(username)
    else:
        gestalt.delete()
        yield CommandResult(f"Removed user '{gestalt}'")


class MatrixCommander:
    def __init__(self):
        self._commander = create_commander("root")
        self._commander.compose(commander, help_command.command)

    def process_command(self, command):
        try:
            for response in self._commander.dispatch(command):
                yield strip_tags(response.message)
        except kien.error.CommandError as exc:
            yield str(exc)
