import getpass

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.management import BaseCommand
from django.core.management.utils import get_random_secret_key

from grouprise.features.associations.models import Association
from grouprise.features.content.models import Content
from grouprise.features.groups.models import Group


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
    def handle(self, *args, **options):
        # site settings
        site_domain = get_input("Site's domain")
        site_name = get_input("Site's (long) name")
        site_short_name = get_input("Site's short name")

        # admin user
        admin_first_name = get_input("Admin first name")
        admin_username = get_input("Admin username", default=admin_first_name.lower())
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

        secret_key = get_random_secret_key()

        # we assume there's only one site
        default_site = Site.objects.first()
        default_site.domain = site_domain
        default_site.name = site_name
        default_site.save()

        operator_group, _ = Group.objects.get_or_create(name=site_short_name)

        if not User.objects.filter(username=admin_username).first():
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
            "* Configure \"Claims\" (see `CLAIMS` in the "
            "[options](https://docs.grouprise.org/configuration/options.html#grouprise-options)).",
            public=False,
            pinned=True,
        )

        # TODO: replace with template
        print(
            f"""
Integrate the following lines into your grouprise settings file:

SECRET_KEY = "{secret_key}"
ALLOWED_HOSTS = ["localhost", "{site_domain}"]
ADMINS = [("{admin_first_name}", "{admin_email}")]
DEFAULT_FROM_EMAIL = "noreply@{site_domain}"
SERVER_EMAIL = "noreply@{site_domain}"

GROUPRISE = {{
    "OPERATOR_GROUP_ID": {operator_group.id},
    "UNKNOWN_GESTALT_ID": {unknown_user.id},
    "FEED_IMPORTER_GESTALT_ID": {import_user.id},
    "DEFAULT_DISTINCT_FROM_EMAIL": "noreply+{{slug}}@{site_domain}",
    "DEFAULT_REPLY_TO_EMAIL": "reply+{{reply_key}}@{site_domain}",
    "POSTMASTER_EMAIL": "postmaster@{site_domain}",
}}
"""
        )
