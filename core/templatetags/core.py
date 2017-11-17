import os
import html
import json

import bleach as python_bleach

from core import fragments, markdown as core_markdown
from core.views import app_config
from django import apps, template
from django.conf import settings
from django.contrib.sites import models as sites_models
from django.template import defaultfilters
from django.template.base import FilterExpression
from django.template.loader import get_template
from django.utils import html as django_html, safestring
import markdown as python_markdown
from markdown.extensions import toc
from core.assets import get_assets

register = template.Library()


@register.inclusion_tag('core/_field.html')
def field(form_field, **kwargs):
    kwargs['field'] = form_field
    return kwargs


@register.inclusion_tag('core/_checkbox_field.html')
def field_checkbox(form_field, **kwargs):
    kwargs['field'] = form_field
    return kwargs


@register.simple_tag
def get(d, *args):
    for i in args:
        try:
            d = d.get(i)
        except AttributeError:
            pass
    return d


@register.filter
def filename(value, include_ext=True):
    base = os.path.basename(getattr(value, 'name', value))
    return base if include_ext else os.path.splitext(base)[0]


@register.filter
def endswith(value: str, search):
    return value.endswith(search)


@register.filter
def startswith(value: str, search):
    return value.startswith(search)


@register.filter
def nolinebreaks(value):
    return ' '.join(str(value).split('\n'))


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


@register.inclusion_tag('stadt/_menu.html', takes_context=True)
def menu(context, active=None, entity=None):
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
    def wrap(result):
        if plain_preview:
            return result
        else:
            script = """
            <script type='text/markdown' data-original-content>{}</script>
            """.format(json.dumps(html.escape(text)))
            return "<div>{}{}</div>".format(script, result)
    extensions = tuple(core_markdown.markdown_extensions) + (
            toc.TocExtension(baselevel=heading_baselevel, marker='[INHALT]'), )
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
        result = django_html.conditional_escape(result)

    return safestring.mark_safe(wrap(result))


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
        self.label = safestring.mark_safe(label)
        self.nodelist = nodelist

    def render(self, context):
        context['dropdown_id'] = self.name
        context['dropdown_label'] = self.label
        context['dropdown_items'] = self.nodelist.render(context)
        return context.template.engine.get_template('core/_dropdown.html').render(context)


@register.filter
def connect(val1, val2):
    return val1, val2


@register.filter
def cuttrailing(s1, s2):
    if s1.endswith(s2):
        return s1[:-len(s2)]
    return s1


@register.filter
def limit(indexable, count):
    return indexable[:count]


@register.filter
def override(override, overridden):
    if type(override) == type(overridden):
        return override
    else:
        return overridden


@register.filter
def url_for(gestalt, user):
    if user.has_perm('entities.view_gestalt', gestalt):
        return gestalt.get_profile_url()
    else:
        return gestalt.get_contact_url()


@register.simple_tag(takes_context=True)
def include_features(context, template_name):
    result = ''
    for app in apps.apps.get_app_configs():
        try:
            t = context.template.engine.get_template('{}/{}'.format(app.label, template_name))
            result += t.render(context)
        except template.TemplateDoesNotExist:
            pass
    return safestring.mark_safe(result)


def parse_token_args(args, filterval=lambda value: value):
    result_kwargs = {}
    result_args = []

    for arg in args:
        if '=' in arg:
            name, value = arg.split('=')
            result_kwargs[name] = filterval(value)
        else:
            result_args.append(filterval(arg))
    return result_args, result_kwargs


def _setup_macros_dict(parser):
    # Metadata of each macro are stored in a new attribute
    # of 'parser' class. That way we can access it later
    # in the template when processing 'usemacro' tags.
    try:
        # Only try to access it to eventually trigger an exception
        parser._macros
    except AttributeError:
        parser._macros = {}


class DefineMacroNode(template.Node):
    def __init__(self, name, nodelist, args):

        self.name = name
        self.nodelist = nodelist
        self.args, self.kwargs = parse_token_args(args)

    def render(self, context):
        # empty string - {% macro %} tag does no output
        return ''


@register.tag(name="kwacro")
def do_macro(parser, token):
    try:
        args = token.split_contents()
        macro_name, args = args[1], args[2:]
    except IndexError:
        m = ("'%s' tag requires at least one argument (macro name)"
             % token.contents.split()[0])
        raise template.TemplateSyntaxError(m)
    # TODO: could do some validations here,
    # for now, "blow your head clean off"
    nodelist = parser.parse(('endkwacro', ))
    parser.delete_first_token()

    # Metadata of each macro are stored in a new attribute
    # of 'parser' class. That way we can access it later
    # in the template when processing 'usemacro' tags.
    _setup_macros_dict(parser)
    parser._macros[macro_name] = DefineMacroNode(macro_name, nodelist, args)
    return parser._macros[macro_name]


class LoadMacrosNode(template.Node):
    def render(self, context):
        # empty string - {% loadmacros %} tag does no output
        return ''


@register.tag(name="loadkwacros")
def do_loadmacros(parser, token):
    try:
        tag_name, filename = token.split_contents()
    except IndexError:
        m = ("'%s' tag requires at least one argument (macro name)"
             % token.contents.split()[0])
        raise template.TemplateSyntaxError(m)
    if filename[0] in ('"', "'") and filename[-1] == filename[0]:
        filename = filename[1:-1]
    t = get_template(filename)
    macros = t.nodelist.get_nodes_by_type(DefineMacroNode)
    # Metadata of each macro are stored in a new attribute
    # of 'parser' class. That way we can access it later
    # in the template when processing 'usemacro' tags.
    _setup_macros_dict(parser)
    for macro in macros:
        parser._macros[macro.name] = macro
    return LoadMacrosNode()


class UseMacroNode(template.Node):

    def __init__(self, macro, fe_args, fe_kwargs):
        self.macro = macro
        self.fe_args = fe_args
        self.fe_kwargs = fe_kwargs

    def render(self, context):
        for i, arg in enumerate(self.macro.args):
            try:
                fe = self.fe_args[i]
                context[arg] = fe.resolve(context)
            except IndexError:
                context[arg] = ""
        for name, default in iter(self.macro.kwargs.items()):
            if name in self.fe_kwargs:
                context[name] = self.fe_kwargs[name].resolve(context)
            else:
                context[name] = FilterExpression(default,
                                                 self.macro.parser
                                                 ).resolve(context)
        return self.macro.nodelist.render(context)


@register.tag(name="usekwacro")
def do_usemacro(parser, token):
    try:
        args = token.split_contents()
        macro_name, values = args[1], args[2:]
    except IndexError:
        m = ("'%s' tag requires at least one argument (macro name)"
             % token.contents.split()[0])
        raise template.TemplateSyntaxError(m)
    try:
        macro = parser._macros[macro_name]
    except (AttributeError, KeyError):
        m = "Macro '%s' is not defined" % macro_name
        raise template.TemplateSyntaxError(m)

    fe_args, fe_kwargs = parse_token_args(values, lambda value: FilterExpression(value, parser))
    macro.parser = parser
    return UseMacroNode(macro, fe_args, fe_kwargs)
