import re

import django

from features.gestalten.models import Gestalt
from features.groups.models import Group


EMAIL_RE = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-.]+'


class Command(django.core.management.base.BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('group_slug')
        parser.add_argument('creator_username')
        parser.add_argument('emails_filename')

    def handle(self, *args, **options):
        try:
            num_new_members = 0
            group = Group.objects.get(slug=options['group_slug'])
            creator = Gestalt.objects.get(user__username=options['creator_username'])
            emails = re.findall(EMAIL_RE, (open(options['emails_filename']).read()))
            for email in emails:
                gestalt = Gestalt.objects.get_or_create_by_email(email)
                try:
                    group.memberships.create(member=gestalt, created_by=creator)
                    num_new_members += 1
                except django.db.utils.IntegrityError:
                    self.stderr.write(
                            self.style.WARNING('{} is already member.'.format(email)))
            self.stderr.write(
                    self.style.SUCCESS('Added {} new members.'.format(num_new_members)))
        except Group.DoesNotExist:
            self.stderr.write(
                    self.style.ERROR('Group {} not found.'.format(options['group_slug'])))
        except Gestalt.DoesNotExist:
            self.stderr.write(
                    self.style.ERROR('Gestalt {} not found.'.format(options['creator_username'])))
        except FileNotFoundError:
            self.stderr.write(
                    self.style.ERROR('File {} not found.'.format(options['emails_filename'])))
