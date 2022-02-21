import datetime
import difflib
import functools
import os
import re
from typing import Union

from django.utils import timezone
import kien.command.help as help_command
import kien.error
from kien import CommandResult, create_commander, var
from kien.transformation import transform
from kien.utils import strip_tags
from kien.validation import is_gt, is_int, validate

from grouprise.core.settings import get_grouprise_baseurl, CORE_SETTINGS
from grouprise.features.associations.models import Association
from grouprise.features.contributions.models import Contribution
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups.models import Group
from grouprise.features.memberships.models import Membership

commander = create_commander("grouprise-commander")


TIME_FORMAT = "%Y-%m-%d %H:%M"


class MatrixCommanderResult(CommandResult):
    """this derived class helps us distinguish kien messages from our own messages

    Without this separate class, we could not excempt kien's messages from being interpreted as
    markdown.
    """


class ResolveException(Exception):
    """we failed to resolve an item (user, group, content, ...)"""

    def __init__(self, message_lines, *args, **kwargs):
        if isinstance(message_lines, str):
            message_lines = [message_lines]
        self._msg_lines = tuple(message_lines)
        super().__init__(self, os.linesep.join(self._msg_lines))

    def get_command_results(self):
        for line in self._msg_lines:
            yield MatrixCommanderResult(line, success=False)


def _get_invalid_key_response(invalid_key, label, alternatives, max_alternative_count):
    yield f"Unknown {label}: {invalid_key}"
    closest_matches = difflib.get_close_matches(
        invalid_key, alternatives, max_alternative_count
    )
    if closest_matches:
        yield "Maybe you meant one of the following?"
        yield ""
        for item in closest_matches:
            yield "- " + item


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
            # one conversion was successful
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
        yield MatrixCommanderResult(f"Added *{gestalt}* to group *{group}*")
    else:
        yield MatrixCommanderResult(
            f"**Warning**: user *{gestalt}* is already a member of group *{group}*",
            success=False,
        )


@commander(user, "leave", var("username"), var("groupname"))
@inject_resolved(source="username", target="gestalt", resolvers=[get_gestalt])
@inject_resolved(source="groupname", target="group", resolvers=[get_group])
def user_leave_group(gestalt: Gestalt, group: Group):
    queryset = Membership.objects.filter(member=gestalt, group=group)
    if queryset.exists():
        queryset.delete()
        yield MatrixCommanderResult(f"Removed *{gestalt}* from group *{group}*")
    else:
        yield MatrixCommanderResult(
            f"**Failure**: user *{gestalt}* is not a member of group *{group}*",
            success=False,
        )


def get_unused_gestalts(
    limit: int = None,
    acount_creation_age_days: int = 30,
):
    # The first login happens automatically right after registration.  We use this short time frame
    # for determining whether a user logged in only once at all (during registration).
    login_after_registration_time = datetime.timedelta(seconds=60)
    if acount_creation_age_days is None:
        recent_account_creation_time = None
    else:
        recent_account_creation_time = timezone.now() - datetime.timedelta(
            days=acount_creation_age_days
        )
    gestalt_exemptions = {
        CORE_SETTINGS.FEED_IMPORTER_GESTALT_ID,
        CORE_SETTINGS.UNKNOWN_GESTALT_ID,
    }
    count = 0
    queryset = Gestalt.objects.filter(
        associations=None,
        contributions=None,
        groups=None,
        images=None,
        memberships=None,
        subscriptions=None,
        versions=None,
        votes=None,
    )
    if recent_account_creation_time is not None:
        # the account was registered recently - maybe there will be the first login soon
        queryset = queryset.filter(user__date_joined__lt=recent_account_creation_time)
    for gestalt in queryset.order_by("activity_bookmark_time").prefetch_related("user"):
        # test a few exceptions - all remaining accounts should be disposable
        if gestalt.pk in gestalt_exemptions:
            # some users are relevant for grouprise itself
            continue
        # did the user log in again, later (after the registration)?
        if gestalt.user.last_login and (
            (gestalt.user.last_login - gestalt.user.date_joined)
            > login_after_registration_time
        ):
            # the user logged in at least twice - it seems to be human
            continue
        # TODO: the test for "can_login" excludes most accounts from automatic removal.
        #    Maybe we should not trust this condition?
        if gestalt.can_login():
            # the confirmation email was processed by the user
            continue
        # this seems to be really a bot (or an unused account)
        yield gestalt
        count += 1
        if (limit is not None) and (count >= limit):
            break


@commander(user, "list-unused", var("limit", is_optional=True))
@validate(limit=(is_int() & is_gt(0)))
@transform(limit=int)
def user_list_unused(limit):
    if limit is None:
        limit = 5
    unused_gestalts = list(get_unused_gestalts())
    yield MatrixCommanderResult(f"There are {len(unused_gestalts)} unused accounts.")
    yield MatrixCommanderResult(f"The {limit} most recently active ones are:")
    yield MatrixCommanderResult("")
    for gestalt in unused_gestalts[:limit]:
        date_joined = gestalt.user.date_joined.strftime(TIME_FORMAT)
        date_activity = gestalt.activity_bookmark_time.strftime(TIME_FORMAT)
        yield MatrixCommanderResult(
            f"- {gestalt.user.username}"
            f" (joined: {date_joined}, activity: {date_activity})"
        )


@commander(user, "remove-unused", var("limit", is_optional=True))
@validate(limit=(is_int() & is_gt(0)))
@transform(limit=int)
def user_remove_unused(limit):
    if limit is None:
        limit = 5
    yield MatrixCommanderResult("Removed the following accounts:")
    yield MatrixCommanderResult("")
    for gestalt in get_unused_gestalts(limit):
        username = gestalt.user.username
        gestalt.delete()
        yield MatrixCommanderResult(f"- {username}")


@commander(user, "show", var("username"))
@inject_resolved(source="username", target="gestalt", resolvers=[get_gestalt])
def show_user(gestalt: Gestalt):
    yield MatrixCommanderResult(f"- *Username*: {gestalt.user.username}")
    yield MatrixCommanderResult(f"- *Email*: {gestalt.user.email}")
    yield MatrixCommanderResult(f"- *Contributions*: {gestalt.contributions.count()}")
    yield MatrixCommanderResult(f"- *Group memberships*: {gestalt.memberships.count()}")
    latest_contribution = gestalt.contributions.order_by("time_created").last()
    if latest_contribution:
        timestamp = latest_contribution.time_created.strftime(TIME_FORMAT)
    else:
        timestamp = None
    yield MatrixCommanderResult(f"- *Latest contribution*: {timestamp}")


@commander(user, "remove", var("username"))
@inject_resolved(source="username", target="gestalt", resolvers=[get_gestalt])
def remove_user(gestalt):
    gestalt.delete()
    yield MatrixCommanderResult(f"Removed user *{gestalt}*")


@commander("group", is_abstract=True)
def group():
    pass


@commander(group, "show", var("groupname"))
@inject_resolved(source="groupname", target="group", resolvers=[get_group])
def group_show(group):
    open_text = "open" if group.closed else "closed"
    url = get_grouprise_baseurl().rstrip("/") + group.get_absolute_url()
    yield MatrixCommanderResult(f"- Group [{group.name}]({url}) is {open_text}")
    yield MatrixCommanderResult(f"- *Members*: {group.members.count()}")
    yield MatrixCommanderResult(f"- *Subscribers*: {group.subscribers.count()}")
    yield MatrixCommanderResult(f"- *Content*: {group.associations.count()}")
    latest_activity_time = group.get_latest_activity_time()
    if latest_activity_time:
        timestamp = latest_activity_time.strftime(TIME_FORMAT)
    else:
        timestamp = None
    yield MatrixCommanderResult(f"- *Latest activity*: {timestamp}")


@commander(group, "remove", var("groupname"))
@inject_resolved(source="groupname", target="group", resolvers=[get_group])
def group_delete(group):
    old_group_name = str(group)
    group.delete()
    yield MatrixCommanderResult(f"Removed group *{old_group_name}*")


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
    if (
        (len(tokens) == 3)
        and (tokens[0] == "stadt")
        and (tokens[1] in {"content", "conversations"})
    ):
        # see URL "content-permalink"
        try:
            association_pk = int(tokens[2])
        except ValueError:
            raise not_found_exception
        else:
            try:
                return Association.objects.get(pk=association_pk)
            except Association.DoesNotExist:
                raise not_found_exception
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
        yield MatrixCommanderResult(
            f"Invalid target state: `{state}` (should be `public` or `private`)",
            success=False,
        )
        return
    if should_go_public:
        association.public = True
    else:
        association.public = False
    association.save()
    yield MatrixCommanderResult(
        f"Changed visibility to *{'public' if should_go_public else 'private'}*"
    )


@commander(content, "remove", var("url"))
@inject_resolved(source="url", target="association", resolvers=[get_association_by_url])
def remove_content(association: Association):
    association_description = str(association)
    association.delete()
    yield MatrixCommanderResult(f"Removed content: {association_description}")


@commander(content, "ownership", var("url"), var("group_or_user"))
@inject_resolved(source="url", target="association", resolvers=[get_association_by_url])
@inject_resolved(
    source="group_or_user", target="entity", resolvers=[get_group, get_gestalt]
)
def change_content_ownership(association: Association, entity: Union[Gestalt, Group]):
    previous_owner = association.entity
    if previous_owner == entity:
        yield MatrixCommanderResult(
            f"**Warning**: the content *{association}* already belongs to *{entity}*",
            success=False,
        )
    else:
        association.entity = entity
        association.save()
        yield MatrixCommanderResult(
            f"Changed ownership of *{association}* from *{previous_owner}* to *{entity}*"
        )


@commander("comment", is_abstract=True)
def contribution():
    pass


def get_contribution_by_url(url):
    """retrieve a contribution instance based on an URL

    example URL: https://example.org/stadt/content/42/#contribution-23
    """
    not_found_exception = ResolveException(
        f"Failed to find comment based on URL ('{url}'). Maybe try the permanent link?"
    )
    contribution_regex = r"/#contribution-(\d+)$"
    contribution_match = re.search(contribution_regex, url)
    if contribution_match:
        contribution_id = int(contribution_match.groups()[0])
        try:
            return Contribution.objects.get(pk=contribution_id)
        except Contribution.DoesNotExist:
            raise not_found_exception
    else:
        raise not_found_exception


@commander(contribution, "show", var("url"))
@inject_resolved(
    source="url", target="contribution", resolvers=[get_contribution_by_url]
)
def show_contribution(contribution: Contribution, max_text_length: int = 200):
    yield MatrixCommanderResult(f"- *Author*: {contribution.author}")
    time_created = contribution.time_created.strftime(TIME_FORMAT)
    yield MatrixCommanderResult(f"- *Published*: {time_created}")
    full_text = contribution.text.last().text
    if len(full_text) > max_text_length:
        abbreviated_text = full_text[: max_text_length - 1] + " …"
    else:
        abbreviated_text = full_text
    yield MatrixCommanderResult(f"- *Content*: {abbreviated_text}")


@commander(contribution, "remove", var("url"))
@inject_resolved(
    source="url", target="contribution", resolvers=[get_contribution_by_url]
)
def delete_contribution(contribution: Contribution):
    # remember the contribution ID before deleting the object
    old_identifier = contribution.pk
    contribution.delete()
    yield MatrixCommanderResult(f"Removed comment `#{old_identifier}`")


@commander(user, "admin", "list")
def list_admins():
    for gestalt in Gestalt.objects.filter(
        user__is_staff=True, user__is_superuser=True
    ).only("user"):
        yield MatrixCommanderResult(f"- {gestalt.user.username}")


@commander(user, "admin", "grant", var("username"))
@inject_resolved(source="username", target="gestalt", resolvers=[get_gestalt])
def grant_admin(gestalt):
    user = gestalt.user
    if user.is_staff and user.is_superuser:
        yield MatrixCommanderResult(
            f"**Warning**: the user *{gestalt}* is already privileged", success=False
        )
    else:
        user.is_staff = True
        user.is_superuser = True
        user.save()
        yield MatrixCommanderResult(f"Granted privileges to user *{gestalt}*")


@commander(user, "admin", "revoke", var("username"))
@inject_resolved(source="username", target="gestalt", resolvers=[get_gestalt])
def revoke_admin(gestalt):
    user = gestalt.user
    if not user.is_staff and not user.is_superuser:
        yield MatrixCommanderResult(
            f"**Warning**: the user *{gestalt}* is not privileged", success=False
        )
    else:
        user.is_staff = False
        user.is_superuser = False
        user.save()
        yield MatrixCommanderResult(f"Revoked privileges from user *{gestalt}*")


class MatrixCommander:
    def __init__(self):
        self._commander = create_commander("root")
        self._commander.compose(commander, help_command.command)

    def process_command(self, command):
        lines = []
        use_markdown = True
        try:
            for response in self._commander.dispatch(command):
                if not isinstance(response, MatrixCommanderResult):
                    use_markdown = False
                lines.append(strip_tags(response.message))
            return os.linesep.join(lines), use_markdown
        except kien.error.CommandError as exc:
            return str(exc), False
