import difflib
import functools
import os
from typing import Union

import kien.command.help as help_command
import kien.error
from kien import CommandResult, create_commander, var
from kien.utils import strip_tags

from grouprise.core.settings import get_grouprise_baseurl
from grouprise.features.associations.models import Association
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups.models import Group
from grouprise.features.memberships.models import Membership

commander = create_commander("grouprise-commander")


class ResolveException(Exception):
    def __init__(self, message_lines, *args, **kwargs):
        if isinstance(message_lines, str):
            message_lines = [message_lines]
        self._msg_lines = tuple(message_lines)
        super().__init__(self, os.linesep.join(self._msg_lines))

    def get_command_results(self):
        for line in self._msg_lines:
            yield CommandResult(line, success=False)


def _get_invalid_key_response(invalid_key, label, alternatives, max_alternative_count):
    yield f"Unknown {label}: {invalid_key}"
    closest_matches = difflib.get_close_matches(
        invalid_key, alternatives, max_alternative_count
    )
    if closest_matches:
        yield "Maybe you meant one of the following?"
        for item in closest_matches:
            yield "  " + item


def get_unknown_username_response(username, max_alternative_count=10):
    all_usernames = (
        item.user.username for item in Gestalt.objects.only("user__username")
    )
    yield from _get_invalid_key_response(
        username, "username", all_usernames, max_alternative_count
    )


def get_unknown_groupname_response(groupname, max_alternative_count=10):
    all_groupnames = (item.slug for item in Group.objects.only("slug"))
    yield from _get_invalid_key_response(
        groupname, "groupname", all_groupnames, max_alternative_count
    )


def inject_resolved(source, target, resolvers):
    def outer(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            collected_errors = []
            original_value = kwargs.pop(source)
            for resolver in resolvers:
                try:
                    new_value = resolver(original_value)
                except ResolveException as exc:
                    collected_errors.append(exc.get_command_results())
                else:
                    # the conversion is finished successfully
                    kwargs[target] = new_value
                    break
            else:
                # none of the resolvers managed to deliver a result - bail out with the first error
                yield from collected_errors[0]
                return
            # one conversion was successfuly
            yield from func(*args, **kwargs)

        return inner

    return outer


def get_gestalt(name: str) -> Gestalt:
    try:
        return Gestalt.objects.get(user__username=name)
    except Gestalt.DoesNotExist:
        raise ResolveException(get_unknown_username_response(name))


def get_group(slug_or_url: str) -> Group:
    if "/" in slug_or_url:
        # the token in the URL is the group slug
        group_name = slug_or_url.strip("/").split("/")[-1]
    else:
        group_name = slug_or_url
    try:
        return Group.objects.get(slug=group_name)
    except Group.DoesNotExist:
        raise ResolveException(get_unknown_groupname_response(group_name))


@commander("user", is_abstract=True)
def user():
    pass


@commander(user, "join", var("username"), var("groupname"))
@inject_resolved(source="username", target="gestalt", resolvers=[get_gestalt])
@inject_resolved(source="groupname", target="group", resolvers=[get_group])
def user_join_group(gestalt: Gestalt, group: Group):
    if not Membership.objects.filter(member=gestalt, group=group).exists():
        Membership.objects.create(member=gestalt, group=group, created_by=gestalt)
        yield CommandResult(f"Added '{gestalt}' to group '{group}'")
    else:
        yield CommandResult(
            f"Warning: user '{gestalt}' is already a member of group '{group}'",
            success=False,
        )


@commander(user, "leave", var("username"), var("groupname"))
@inject_resolved(source="username", target="gestalt", resolvers=[get_gestalt])
@inject_resolved(source="groupname", target="group", resolvers=[get_group])
def user_leave_group(gestalt: Gestalt, group: Group):
    queryset = Membership.objects.filter(member=gestalt, group=group)
    if queryset.exists():
        queryset.delete()
        yield CommandResult(f"Removed '{gestalt}' from group '{group}'")
    else:
        yield CommandResult(
            f"Failure: user '{gestalt}' is not a member of group '{group}'",
            success=False,
        )


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
@inject_resolved(source="username", target="gestalt", resolvers=[get_gestalt])
def show_user(gestalt: Gestalt):
    yield CommandResult(f"Username: {gestalt.user.username}")
    yield CommandResult(f"Email: {gestalt.user.email}")
    yield CommandResult(f"Contributions: {gestalt.contributions.count()}")
    yield CommandResult(f"Group memberships: {gestalt.memberships.count()}")
    latest_contribution = gestalt.contributions.order_by("time_created").last()
    timestamp = latest_contribution.time_created if latest_contribution else None
    yield CommandResult(f"Latest contribution: {timestamp}")


@commander(user, "remove", var("username"))
@inject_resolved(source="username", target="gestalt", resolvers=[get_gestalt])
def remove_user(gestalt):
    gestalt.delete()
    yield CommandResult(f"Removed user '{gestalt}'")


@commander("content", is_abstract=True)
def content():
    pass


def get_association_by_url(url):
    not_found_exception = ResolveException(
        f"Failed to find content based on URL ('{url}'). Maybe try the permanent link?"
    )
    base_url = get_grouprise_baseurl().rstrip("/")
    url = url.rstrip("/")
    if url.startswith(base_url):
        url = url[len(base_url) :]
    tokens = url.lstrip("/").split("/")
    if (len(tokens) == 3) and (tokens[0] == "stadt") and (tokens[1] == "content"):
        # see URL "content-permalink"
        try:
            association_pk = int(tokens[2])
        except ValueError:
            raise not_found_exception
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
                entity = Gestalt.objects.get(user__username=entity_slug)
            except Gestalt.DoesNotExist:
                raise not_found_exception
        for association in Association.objects.filter(slug=association_slug):
            if association.entity == entity:
                return association
        else:
            raise not_found_exception
    else:
        raise not_found_exception


@commander(content, "visibility", var("url"), var("state"))
@inject_resolved(source="url", target="association", resolvers=[get_association_by_url])
def change_content_visibility(association: Association, state: str):
    if state.lower() == "public":
        should_go_public = True
    elif state.lower() == "private":
        should_go_public = False
    else:
        yield CommandResult(
            f"Invalid target state: {state} (should be 'public' or 'private')"
        )
        return
    if should_go_public:
        association.public = True
    else:
        association.public = False
    association.save()
    yield CommandResult(
        f"Changed visibility to {'public' if should_go_public else 'private'}"
    )


@commander(content, "ownership", var("url"), var("group_or_user"))
@inject_resolved(source="url", target="association", resolvers=[get_association_by_url])
@inject_resolved(
    source="group_or_user", target="entity", resolvers=[get_group, get_gestalt]
)
def change_content_ownership(association: Association, entity: Union[Gestalt, Group]):
    previous_owner = association.entity
    if previous_owner == entity:
        yield CommandResult(
            f"Warning: the content '{association}' already belongs to '{entity}'",
            success=False,
        )
    else:
        association.entity = entity
        association.save()
        yield CommandResult(
            f"Changed ownership of '{association}' from '{previous_owner}' to '{entity}'"
        )


@commander(user, "admin", "list")
def list_admins():
    for gestalt in Gestalt.objects.filter(
        user__is_staff=True, user__is_superuser=True
    ).only("user"):
        yield CommandResult(f"{gestalt.user.username}")


@commander(user, "admin", "grant", var("username"))
@inject_resolved(source="username", target="gestalt", resolvers=[get_gestalt])
def grant_admin(gestalt):
    user = gestalt.user
    if user.is_staff and user.is_superuser:
        yield CommandResult(
            f"Warning: the user '{gestalt}' is already privileged", success=False
        )
    else:
        user.is_staff = True
        user.is_superuser = True
        user.save()
        yield CommandResult(f"Granted privileges to user '{gestalt}'")


@commander(user, "admin", "revoke", var("username"))
@inject_resolved(source="username", target="gestalt", resolvers=[get_gestalt])
def revoke_admin(gestalt):
    user = gestalt.user
    if not user.is_staff and not user.is_superuser:
        yield CommandResult(
            f"Warning: the user '{gestalt}' is not privileged", success=False
        )
    else:
        user.is_staff = False
        user.is_superuser = False
        user.save()
        yield CommandResult(f"Revoked privileges from user '{gestalt}'")


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
