import copy
import getpass

import ruamel.yaml
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.core.management.utils import get_random_secret_key

from grouprise.core.settings import get_grouprise_site
from grouprise.features.associations.models import Association
from grouprise.features.content.models import Content
from grouprise.features.groups.models import Group
from grouprise.settings_loader import load_settings_from_yaml_files


def get_input(prompt, default=None):
    result = input("{}{}: ".format(prompt, f" ({default})" if default else ""))
    return result if result else default


def create_article(author, group, slug, title, text, public=True, pinned=False):
    article = Content.objects.create(title=title)
    article.versions.create(author=author, text=text)
    association = Association(slug=slug, public=public, pinned=pinned)
    association.entity = group
    association.container = article
    association.save()


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

        site = get_grouprise_site()
        # site settings
        site_domain = get_input(
            "Site's domain", default=original_settings.get("domain", site.domain)
        )
        site_name = get_input("Site's (long) name", default=site.name)
        site_short_name = get_input("Site's short name")

        # admin user
        admin_first_name = get_input("Admin first name (empty -> skip)")
        if admin_first_name:
            admin_username = get_input(
                "Admin username", default=admin_first_name.lower()
            )
            admin_email = get_input("Admin email")
            admin_password = getpass.getpass("Admin password: ")

        # unknown user
        unknown_name = get_input(
            "Unknown user's display name", default="Unbekannte Gestalt"
        )
        unknown_username = get_input("Unknown user's username", default="unknown")
        unknown_email = get_input(
            "Unknown user's email", default=f"{unknown_username}@{site_domain}"
        )

        # import user
        import_name = get_input(
            "Import user's display name", default="Automatischer Import"
        )
        import_username = get_input("Import user's username", default="import")
        import_email = get_input(
            "Import user's email", default=f"{import_username}@{site_domain}"
        )

        secret_key = original_settings.get("secret_key", get_random_secret_key())

        # we assume there's only one site
        site.domain = site_domain
        site.name = site_name
        site.save()

        operator_group, _ = Group.objects.get_or_create(name=site_short_name)

        if (
            admin_first_name
            and not User.objects.filter(username=admin_username).first()
        ):
            User.objects.create_superuser(
                username=admin_username,
                first_name=admin_first_name,
                email=admin_email,
                password=admin_password,
            )

        unknown_user, _ = User.objects.get_or_create(
            username=unknown_username, email=unknown_email, first_name=unknown_name
        )

        import_user, _ = User.objects.get_or_create(
            username=import_username, email=import_email, first_name=import_name
        )

        # TODO: allow multiple runs (idempotency) without throwing `IntegrityError`
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
        if admin_email not in original_settings.get("log_recipient_emails", []):
            target_settings.setdefault("log_recipient_emails", [])
            target_settings["log_recipient_emails"].append(admin_email)

        if target_settings != original_target_settings:
            with open(options["modifiable_config"], "w") as output_file:
                ruamel.yaml.YAML().dump(target_settings, output_file)
