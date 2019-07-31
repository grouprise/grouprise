from django import template
from django.db.models import Max


register = template.Library()


@register.filter
def unread(association, gestalt):
    last_activity = association.container.contributions.aggregate(Max('time_created'))
    last_activity = last_activity['time_created__max']
    return last_activity >= gestalt.activity_bookmark_time
