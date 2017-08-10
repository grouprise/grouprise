import os

import bleach as python_bleach

from core import fragments, markdown as core_markdown
from core.views import app_config
from django import template
from django.conf import settings
from django.contrib.sites import models as sites_models
from django.template import defaultfilters
from django.utils import html, safestring
import markdown as python_markdown
from markdown.extensions import toc
from core.assets import get_assets

register = template.Library()


@register.filter
def filename(value):
    return os.path.basename(value.name)


@register.filter
def endswith(value: str, search):
    return value.endswith(search)


@register.filter
def startswith(value: str, search):
    return value.startswith(search)


@register.simple_tag(takes_context=True)
def get_parameters(context, **kwargs):
    request = context.get('request')
    params = request.GET.copy()
    for k in kwargs:
        params[k] = kwargs.get(k)
    # drop page parameter in case of parameter changes (#373)
    if params != request.GET and 'page' not in kwargs and 'page' in params:
        del params['page']
    return params.urlencode()


@register.simple_tag
def include_assets(stage):
    return safestring.mark_safe('\n'.join([
        asset.create_tag() for asset in get_assets(stage)
    ]))


@register.inclusion_tag('core/_link.html')
def link(model, title=None):
    return {'model': model, 'title': title}


@register.inclusion_tag('core/_time.html')
def time(time, suffix=''):
    return {'suffix': suffix, 'time': time}


@register.inclusion_tag('core/_pagination.html', takes_context=True)
def pagination(context, label):
    context['pagination_label'] = label
    return context


@register.inclusion_tag('core/_breadcrumb.html')
def breadcrumb(*args):
    crumbs = []
    for arg in args[:-1]:
        if isinstance(arg, str):
            crumbs.append((arg, None))
        else:
            crumbs.append((str(arg), arg.get_absolute_url()))
    crumbs.append((str(args[-1]), None))
    return {'crumbs': crumbs}


@register.inclusion_tag('core/_menu.html', takes_context=True)
def menu(context, active, entity=None):
    if entity and entity.is_group:
        context['group'] = entity
    context['menu'] = active
    return context


@register.simple_tag()
def ref(entity):
    try:
        return "%s-%d" % (type(entity).__name__.lower(), entity.id)
    except AttributeError:
        return ""


@register.filter
def full_url(path):
    return '{proto}://{domain}{path}'.format(
            proto=settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL,
            domain=sites_models.Site.objects.get_current().domain,
            path=path)


@register.simple_tag(name='app_config')
def render_app_config():
    return safestring.mark_safe(app_config.serialize())


@register.simple_tag(takes_context=True)
def include_fragments(context, fragment_group):
    result = ''
    group = fragments.groups.get(fragment_group, [])
    for key in group:
        t = context.template.engine.get_template(fragments.fragments[key])
        result += t.render(context)
    return safestring.mark_safe(result)


def bleach(text, disable_tags=tuple(), except_for=tuple()):
    if disable_tags == "all":
        allowed_tags = set()
    else:
        allowed_tags = set(core_markdown.content_allowed_tags) - set(disable_tags)
    if except_for:
        allowed_tags |= set(except_for)
    bleached = python_bleach.clean(
            text, strip=True, tags=allowed_tags,
            attributes=core_markdown.content_allowed_attributes)
    if isinstance(text, safestring.SafeString):
        return safestring.mark_safe(bleached)
    else:
        return bleached


@register.simple_tag
def markdown(
        text, heading_baselevel=1, filter_tags=True, truncate=False, disable_tags="",
        plain_preview=False, preset=None):
    extensions = tuple(core_markdown.markdown_extensions) + (
            toc.TocExtension(baselevel=heading_baselevel), )
    result = python_markdown.markdown(text, extensions=extensions)
    if preset == 'linkonly':
        result = bleach(result, disable_tags='all', except_for=('a',))
    elif filter_tags:
        disabled_tags = tuple(disable_tags.split(","))
        result = bleach(result, disabled_tags)
    if truncate:
        result = defaultfilters.truncatewords_html(result, truncate)
    if plain_preview:
        result = bleach(result, disable_tags="all")
        result = defaultfilters.truncatewords(result, plain_preview)
        result = html.conditional_escape(result)

    return safestring.mark_safe(result)


@register.tag
def dropdown(parser, token):
    try:
        tag_name, name, label = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
                "%r tag requires two arguments" % token.contents.split()[0])
    if not ((name[0] == name[-1] and name[0] in ('"', "'"))
            and (label[0] == label[-1] and label[0] in ('"', "'"))):
        raise template.TemplateSyntaxError(
                "%r tag's arguments should be in quotes" % tag_name)
    nodelist = parser.parse(('enddropdown',))
    parser.delete_first_token()
    return DropdownNode(name[1:-1], label[1:-1], nodelist)


class DropdownNode(template.Node):
    def __init__(self, name, label, nodelist):
        self.name = name
        self.label = label
        self.nodelist = nodelist

    def render(self, context):
        context['dropdown_id'] = self.name
        context['dropdown_label'] = self.label
        context['dropdown_items'] = self.nodelist.render(context)
        return context.template.engine.get_template('core/_dropdown.html').render(context)


@register.tag
def sidebarblock(parser, token):
    try:
        tag_name, title, icon = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
                "%r tag requires two arguments" % token.contents.split()[0])
    if not ((title[0] == title[-1] and title[0] in ('"', "'"))
            and (icon[0] == icon[-1] and icon[0] in ('"', "'"))):
        raise template.TemplateSyntaxError(
                "%r tag's arguments should be in quotes" % tag_name)
    content_nodelist = parser.parse(('actions', 'endsidebarblock',))
    token = parser.next_token()
    if token.contents == 'actions':
        actions_nodelist = parser.parse(('endsidebarblock',))
        parser.delete_first_token()
    else:
        actions_nodelist = None
    return SidebarBlockNode(
            title[1:-1], icon[1:-1], content_nodelist, actions_nodelist)


class SidebarBlockNode(template.Node):
    def __init__(self, title, icon, content_nodelist, actions_nodelist):
        self.title = title
        self.icon = icon
        self.content_nodelist = content_nodelist
        self.actions_nodelist = actions_nodelist

    def render(self, context):
        context['block_title'] = self.title
        context['block_icon'] = self.icon
        context['block_content'] = self.content_nodelist.render(context)
        if self.actions_nodelist:
            context['block_actions'] = self.actions_nodelist.render(context)
        t = context.template.engine.get_template('core/_sidebar_block.html')
        return t.render(context)
