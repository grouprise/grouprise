import copy
import getpass

import ruamel.yaml
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.core.management.utils import get_random_secret_key

from grouprise.core.settings import get_grouprise_site
from grouprise.features.associations.models import Association
from grouprise.features.content.models import Content
from grouprise.features.groups.models import Group
from grouprise.settings_loader import load_settings_from_yaml_files


def get_input(prompt, default=None, previous=None):
    preset = previous if previous is not None else default
    if preset:
        formatted_prompt = f"{prompt} ({preset}): "
    else:
        formatted_prompt = f"{prompt}: "
    result = input(formatted_prompt)
    return result if result else preset


def create_article(author, group, slug, title, text, public=True, pinned=False):
    # look for an existing article
    for assoc in Association.objects.filter(slug=slug, public=public, pinned=pinned):
        if assoc.entity == group:
            return
    else:
        # the article does not exist, yet
        article = Content.objects.create(title=title)
        article.versions.create(author=author, text=text)
        association = Association(slug=slug, public=public, pinned=pinned)
        association.entity = group
        association.container = article
        association.save()


def create_or_update_user(username: str, email: str, first_name: str) -> User:
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User(username=username)
    user.email = email
    user.first_name = first_name
    user.save()
    return user


def get_entity_if_exists(model, entity_id: int):
    if entity_id is None:
        return None
    else:
        try:
            return model.objects.get(pk=entity_id)
        except model.DoesNotExist:
            return None


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--source-config",
            type=str,
            action="append",
            help=(
                "Location of configuration data (directory or filename). "
                "May be specified multiple times",
            ),
        )
        parser.add_argument(
            "--modifiable-config",
            type=str,
            default="/etc/grouprise/conf.d/800-local.yaml",
            help="Path of yaml file to be used for storing settings",
        )

    def handle(self, *args, **options):
        original_settings = load_settings_from_yaml_files(options["source_config"])
        target_settings = load_settings_from_yaml_files([options["modifiable_config"]])
        original_target_settings = copy.copy(target_settings)

        current_operator_group = get_entity_if_exists(
            Group, original_settings.get("operator_group_id")
        )
        current_unknown_user = get_entity_if_exists(
            User, original_settings.get("unknown_gestalt_id")
        )
        current_import_user = get_entity_if_exists(
            User, original_settings.get("feed_importer_gestalt_id")
        )
        current_admin_user = (
            User.objects.filter(is_superuser=True, is_staff=True)
            .order_by("username")
            .first()
        )

        site = get_grouprise_site()
        # site settings
        site_domain = get_input(
            "Site's domain", default=original_settings.get("domain", site.domain)
        )
        site_name = get_input("Site's (long) name", default=site.name)
        site_short_name = get_input(
            "Site's short name",
            previous=getattr(current_operator_group, "name", None),
        )

        # admin user
        admin_first_name = get_input(
            "Admin first name ('none' -> skip)",
            previous=getattr(current_admin_user, "first_name", None),
        )
        skip_admin = admin_first_name == 'none'
        if not skip_admin:
            if current_admin_user and (
                current_admin_user.first_name == admin_first_name
            ):
                default_admin_username = current_admin_user.username
                default_admin_email = current_admin_user.email
            else:
                default_admin_username = admin_first_name.lower()
                default_admin_email = ""
            admin_username = get_input("Admin username", default=default_admin_username)
            admin_email = get_input("Admin email", default=default_admin_email)
            if current_admin_user:
                password_prompt = "Admin password (empty -> do not change): "
            else:
                password_prompt = "Admin password: "
            admin_password = getpass.getpass(password_prompt)

        # unknown user
        unknown_name = get_input(
            "Unknown user's display name",
            default="Unbekannte Gestalt",
            previous=getattr(current_unknown_user, "first_name", None),
        )
        unknown_username = get_input(
            "Unknown user's username",
            default="unknown",
            previous=getattr(current_unknown_user, "username", None),
        )
        unknown_email = get_input(
            "Unknown user's email",
            default=f"{unknown_username}@{site_domain}",
            previous=getattr(current_unknown_user, "email", None),
        )

        # import user
        import_name = get_input(
            "Import user's display name",
            default="Automatischer Import",
            previous=getattr(current_import_user, "first_name", None),
        )
        import_username = get_input(
            "Import user's username",
            default="import",
            previous=getattr(current_import_user, "username", None),
        )
        import_email = get_input(
            "Import user's email",
            default=f"{import_username}@{site_domain}",
            previous=getattr(current_import_user, "email", None),
        )

        secret_key = original_settings.get("secret_key", get_random_secret_key())

        # we assume there's only one site
        site.domain = site_domain
        site.name = site_name
        site.save()

        operator_group, _ = Group.objects.get_or_create(name=site_short_name)

        if not skip_admin:
            if not User.objects.filter(username=admin_username).first():
                # create a new user
                User.objects.create_superuser(
                    username=admin_username,
                    first_name=admin_first_name,
                    email=admin_email,
                    password=admin_password,
                )
            elif admin_password:
                # update the password
                admin_user = User.objects.get(username=admin_username)
                admin_user.password = make_password(admin_password)
                admin_user.save()

        unknown_user = create_or_update_user(
            unknown_username, unknown_email, unknown_name
        )

        import_user = create_or_update_user(import_username, import_email, import_name)

        create_article(
            unknown_user.gestalt,
            operator_group,
            "imprint",
            "Imprint",
            "Create imprint here.",
        )
        create_article(
            unknown_user.gestalt,
            operator_group,
            "about",
            "About",
            "Write a text about this site and the operator group.",
            pinned=True,
        )
        create_article(
            unknown_user.gestalt,
            operator_group,
            "tools",
            "Tools",
            "Write a text how to use the tools on this site.",
            pinned=True,
        )

        create_article(
            unknown_user.gestalt,
            operator_group,
            "wiki",
            "Wiki",
            "# Further Possibilities\n"
            "* Add a description to this group, it will be displayed in the site footer.\n"
            '* Configure "Claims" (see `CLAIMS` in the '
            "[options](https://docs.grouprise.org/configuration/options.html#grouprise-options)).",
            public=False,
            pinned=True,
        )

        # add only changed or new settings to the target dictionary (minimize changes in the file)
        for key, value in {
            "secret_key": secret_key,
            "domain": site_domain,
            "operator_group_id": operator_group.id,
            "unknown_gestalt_id": unknown_user.id,
            "feed_importer_gestalt_id": import_user.id,
        }.items():
            if original_settings.get(key) != value:
                target_settings[key] = value
        if (
            not skip_admin
            and admin_email
            and (admin_email not in original_settings.get("log_recipient_emails", []))
        ):
            target_settings.setdefault("log_recipient_emails", [])
            target_settings["log_recipient_emails"].append(admin_email)

        if target_settings != original_target_settings:
            with open(options["modifiable_config"], "w") as output_file:
                ruamel.yaml.YAML().dump(target_settings, output_file)
