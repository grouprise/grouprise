"""
Copyright 2016-2017 sense.lab e.V. <info@senselab.org>

This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.
"""

import json

from django import template
from django.db import models
from django.template import Library, loader

from ..models import GestaltSetting

register = Library()


@register.simple_tag(name='dismiss', takes_context=True)
def do_dismiss(context, name, category='dismissible', type='button'):
    template_name = 'dismissible/%s.html' % type
    options = {'name': name, 'category': category, 'value': 'dismissed'}

    try:
        dismissible_template = loader.get_template(template_name)
    except template.TemplateDoesNotExist as err:
        message = 'unknown dismissible template "%s"' % template_name
        raise template.TemplateSyntaxError(message) from err

    try:
        options['gestalt'] = context['user'].gestalt.id
    except (AttributeError, KeyError):
        # no user is present, settings cannot be saved
        return ''

    return dismissible_template.render({
        'payload': json.dumps(options)
    })


@register.tag(name='dismissible')
def do_dismissible(parser, token):
    nodelist = parser.parse(('enddismissible',))
    parser.delete_first_token()

    try:
        name = token.split_contents()[1]
    except IndexError:
        raise template.TemplateSyntaxError('please provide a name for the dismissible')

    if name[0] in ['\'', '"']:
        name = name[1:-1]

    return DismissibleNode(name, nodelist)


class DismissibleNode(template.Node):
    def __init__(self, name, nodelist):
        self.name = name
        self.nodelist = nodelist

    def render(self, context):
        try:
            gestalt = context['user'].gestalt
            setting = GestaltSetting.objects.get(gestalt=gestalt, name=self.name)
            should_render = setting.value != 'dismissed'
        except (AttributeError, KeyError, models.ObjectDoesNotExist):
            should_render = True

        if should_render:
            return '<div class="dismissible">%s</div>' % self.nodelist.render(context)
        else:
            return ''
