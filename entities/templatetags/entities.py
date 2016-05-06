from django import template

register = template.Library()

@register.inclusion_tag('entities/_group_avatar.html')
def group_avatar(group):
    return {'group': group}
