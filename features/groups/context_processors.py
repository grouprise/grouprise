from django.conf import settings

from features.groups.models import Group


def groups(request):
    about_group = Group.objects.filter(id=settings.GROUPRISE.get('ABOUT_GROUP_ID')).first()
    return {'about_group': about_group}
