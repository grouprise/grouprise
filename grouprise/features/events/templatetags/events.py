import datetime
import itertools

import django.utils.formats
import django.utils.timezone
from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

from grouprise.features.events.utils import get_requested_time, EventCalendar

register = template.Library()


@register.filter
def day_preview(associations):
    return ', '.join([
        '{}{}'.format(
            '{} '.format(django.utils.formats.time_format(
                django.utils.timezone.localtime(a.container.time)))
            if not a.container.all_day else '',
            a.container.title)
        for a in associations])


@register.simple_tag(takes_context=True)
def event_time(context, event):
    context['event'] = event
    time_str = context.template.engine.get_template('events/_time.html').render(context)
    return time_str.strip()


@register.inclusion_tag('events/_calendar.html', takes_context=True)
def calendar(context, associations, size='preview', component_id=None):
    request = context.get('request')
    try:
        month = int(request.GET.get('month', 0))
        month = max(0, min(month, 12))
    except ValueError:
        month = None
    try:
        year = int(request.GET.get('year', 0))
        year = max(0, year)
    except ValueError:
        year = None
    around = django.utils.timezone.now()
    around = around.replace(
            day=1,
            month=month or around.month,
            year=year or around.year)
    event_associations = associations.filter_events()
    calendar_associations = event_associations.filter(
            content__time__gt=around-datetime.timedelta(weeks=6),
            content__time__lt=around+datetime.timedelta(weeks=6)
            ).order_by('content__time')
    calendar_event_dict = {date: list(events) for date, events in itertools.groupby(
        calendar_associations, key=lambda a: a.container.time.astimezone().date())}
    calendar = EventCalendar(calendar_event_dict)
    last_month = around.replace(day=1) + datetime.timedelta(days=-1)
    next_month = around.replace(day=1) + datetime.timedelta(days=31)
    context.update({
            'days': calendar.formatweekheader(),
            'prev_month': last_month,
            'month': calendar.formatmonthname(around.year, around.month),
            'next_month': next_month,
            'weeks': calendar.formatmonthweeks(around.year, around.month),
            'size': size,
            'component_id': component_id,
            })
    return context


@register.inclusion_tag('events/_sidebar_calendar.html', takes_context=True)
def sidebar_calendar(
        context, associations, group=None, preview_length=5, show_group=True,
        hide_buttons=False, component_id=None, site_calendar=False):
    user = context['user']
    group = context.get('group')
    upcoming = associations\
        .filter_upcoming(get_requested_time(context.request))\
        .order_by('content__time')[:preview_length]

    # collect toolbar actions
    actions = []
    if (not user.is_authenticated
            or not group and user.has_perm('content.create')
            or user.has_perm('content.group_create', group)):
        url = reverse('create-event')
        if group:
            url = reverse('create-group-event', args=(group.slug,))
        actions.append((mark_safe('<i class="sg sg-add"></i> Veranstaltung eintragen'), url))
    if upcoming:
        url = reverse('events')
        if group:
            url = '{}?content=events'.format(group.get_absolute_url())
        actions.append(('Alle Veranstaltungen', url))
    if group:
        url = reverse('group-events-export', args=(group.slug,))
        actions.append(('Kalender exportieren', url))
    if site_calendar:
        url = reverse('export-site-events')
        actions.append(('Kalender exportieren', url))

    context.update({
        'actions': actions,
        'associations': associations,
        'group': group,
        'hide_buttons': hide_buttons,
        'show_group': show_group,
        'upcoming': upcoming,
        'component_id': component_id
    })
    return context
