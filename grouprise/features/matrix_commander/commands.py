import difflib
import os

from grouprise.features.associations.models import Association
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups.models import Group
from grouprise.core.settings import get_grouprise_baseurl

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
def user():
    pass


@commander(user, "list", "unused", var("limit", is_optional=True))
def user_list_unused(limit: int = 5):
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


@commander(user, "show", var("username"))
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


@commander(user, "remove", var("username"))
def remove_user(username):
    try:
        gestalt = Gestalt.objects.get(user__username=username)
    except Gestalt.DoesNotExist:
        yield from get_unknown_username_response(username)
    else:
        gestalt.delete()
        yield CommandResult(f"Removed user '{gestalt}'")


@commander("content", is_abstract=True)
def content():
    pass


def get_association_by_url(url):
    base_url = get_grouprise_baseurl().rstrip("/")
    url = url.rstrip("/")
    if url.startswith(base_url):
        url = url[len(base_url) :].lstrip("/")
    tokens = url.split("/")
    if (len(tokens) == 3) and (tokens[0] == "stadt") and (tokens[1] == "content"):
        # see URL "content-permalink"
        try:
            association_pk = int(tokens[2])
        except ValueError:
            return None
        else:
            return Association.objects.get(pk=association_pk)
    elif len(tokens) == 2:
        # see URL "content"
        entity_slug = tokens[0]
        association_slug = tokens[1]
        try:
            entity = Group.objects.get(slug=entity_slug)
        except Group.DoesNotExist:
            try:
                entity = Gestalt.objects.get(slug=entity_slug)
            except Gestalt.DoesNotExist:
                return None
        for association in Association.objects.filter(slug=association_slug):
            if association.entity == entity:
                return association
        else:
            return None
    else:
        return None


@commander(content, "visibility", var("url"), var("state"))
def change_content_visibility(url, state):
    if state.lower() == "public":
        should_go_public = True
    elif state.lower() == "private":
        should_go_public = False
    else:
        yield CommandResult(
            f"Invalid target state: {state} (should be 'public' or 'private')"
        )
        return
    association = get_association_by_url(url)
    if association is None:
        yield CommandResult(
            f"Failed to find content based on URL ('{url}'). Maybe try the permanent link?"
        )
    else:
        if should_go_public:
            association.public = True
        else:
            association.public = False
        association.save()
        yield CommandResult(
            f"Changed visibility to {'public' if should_go_public else 'private'}"
        )


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
