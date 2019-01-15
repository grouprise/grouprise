from features.groups.models import Group


def groups(request):
    return {'about_group': Group.objects.operator_group()}
