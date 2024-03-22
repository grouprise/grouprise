import html
import json
import random
from typing import Iterable, Literal, Union

import bleach as python_bleach
import markdown as python_markdown
from django import template
from django.template import defaultfilters
from django.template.base import FilterExpression
from django.template.loader import get_template
from django.utils import html as django_html
from django.utils import safestring
from markdown.extensions import toc

from grouprise.core import markdown as core_markdown
from grouprise.core.views import app_config

from . import Link

register = template.Library()

NON_INTERACTIVE_INLINE_TAGS = [
    "b",
    "big",
    "i",
    "small",
    "tt",
    "abbr",
    "acronym",
    "cite",
    "code",
    "dfn",
    "em",
    "kbd",
    "strong",
    "samp",
    "var",
    "br",
    "q",
    "s",
    "span",
    "sub",
    "sup",
]


@register.inclusion_tag("core/_field.html")
def field(form_field, **kwargs):
    """Render a form field."""
    kwargs["field"] = form_field
    return kwargs


@register.inclusion_tag("core/_checkbox_field.html")
def field_checkbox(form_field, **kwargs):
    """Render a checkbox form field."""
    kwargs["field"] = form_field
    return kwargs


@register.simple_tag(name="random")
def random_item(_list):
    """Choose a random item from the given list."""
    try:
        return random.choice(_list)
    except IndexError:
        return None


@register.simple_tag(takes_context=True)
def get_parameters(context, **kwargs):
    """Render parameters of current url."""
    request = context.get("request")
    params = request.GET.copy()
    for k in kwargs:
        params[k] = str(kwargs.get(k))
    # drop page parameter in case of parameter changes (#373)
    if params != request.GET and "page" not in kwargs and "page" in params:
        del params["page"]
    return params.urlencode()


@register.inclusion_tag("core/_link.html", takes_context=True)
def link(context, model, title=None):
    """Render a link to the given model."""
    if hasattr(model, "get_absolute_url_for_user"):
        url = model.get_absolute_url_for_user(context.get("user"))
    else:
        url = model.get_absolute_url()
    return {"model": model, "title": title, "url": url}


@register.inclusion_tag("core/_time.html")
def time(time, all_day=False, suffix=""):
    return {"all_day": all_day, "suffix": suffix, "time": time}


@register.inclusion_tag("core/_pagination.html", takes_context=True)
def pagination(context, label):
    context["pagination_label"] = label
    return context


@register.inclusion_tag("core/_breadcrumb.html", takes_context=True)
def breadcrumb(context, *args):
    crumbs = []
    for arg in args[:-1]:
        if isinstance(arg, str):
            crumbs.append((arg, None))
        elif isinstance(arg, Link):
            crumbs.append(arg)
        elif hasattr(arg, "get_absolute_url_for_user"):
            crumbs.append(
                (str(arg), arg.get_absolute_url_for_user(context.get("user")))
            )
        else:
            crumbs.append((str(arg), arg.get_absolute_url()))
    crumbs.append((str(args[-1]), None))
    return {"crumbs": crumbs}


@register.inclusion_tag("stadt/_menu.html", takes_context=True)
def menu(context, entity=None):
    if entity and entity.is_group:
        context["group"] = entity
    return context


@register.simple_tag()
def ref(entity):
    try:
        return "%s-%d" % (type(entity).__name__.lower(), entity.id)
    except AttributeError:
        return ""


@register.simple_tag(name="app_config")
def render_app_config():
    return safestring.mark_safe(app_config.serialize())


def bleach(
    text,
    disable_tags: Union[Literal["all"], Iterable[str]] = tuple(),
    except_for: Iterable[str] = tuple(),
):
    if disable_tags == "all":
        allowed_tags = set()
    else:
        allowed_tags = set(core_markdown.content_allowed_tags) - set(disable_tags)
    if except_for:
        allowed_tags |= set(except_for)
    bleached = python_bleach.clean(
        text,
        strip=True,
        tags=allowed_tags,
        attributes=core_markdown.content_allowed_attributes,
    )
    if isinstance(text, safestring.SafeString):
        return safestring.mark_safe(bleached)
    else:
        return bleached


@register.simple_tag
def markdown(
    text,
    heading_baselevel=1,
    filter_tags=True,
    truncate=False,
    disable_tags="",
    plain_preview=False,
    preset=None,
    plain=False,
):
    def wrap(result):
        if plain or plain_preview or truncate:
            return result
        else:
            script = """
            <script type='text/markdown' data-original-content>{}</script>
            """.format(
                json.dumps(html.escape(text))
            )
            return "<div>{}{}</div>".format(script, result)

    extensions = tuple(core_markdown.markdown_extensions) + (
        toc.TocExtension(baselevel=heading_baselevel, marker="[INHALT]"),
    )
    # TODO this needs careful optimization
    #      for every content preview we’re rendering the whole content
    #      to html, then strip html tags and finally truncate the
    #      result just in order to get some partially formatted text
    result = python_markdown.markdown(text, extensions=extensions)
    if preset == "linkonly":
        result = bleach(result, disable_tags="all", except_for=("a", "span"))
    elif preset == "noninteractive-inline":
        result = bleach(
            result, disable_tags="all", except_for=NON_INTERACTIVE_INLINE_TAGS
        )
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
            "%r tag requires two arguments" % token.contents.split()[0]
        )
    if not (
        (name[0] == name[-1] and name[0] in ('"', "'"))
        and (label[0] == label[-1] and label[0] in ('"', "'"))
    ):
        raise template.TemplateSyntaxError(
            "%r tag's arguments should be in quotes" % tag_name
        )
    nodelist = parser.parse(("enddropdown",))
    parser.delete_first_token()
    return DropdownNode(name[1:-1], label[1:-1], nodelist)


class DropdownNode(template.Node):
    def __init__(self, name, label, nodelist):
        self.name = name
        self.label = safestring.mark_safe(label)
        self.nodelist = nodelist

    def render(self, context):
        context["dropdown_id"] = self.name
        context["dropdown_label"] = self.label
        context["dropdown_items"] = self.nodelist.render(context)
        return context.template.engine.get_template("core/_dropdown.html").render(
            context
        )


def parse_token_args(args, filterval=lambda value: value):
    result_kwargs = {}
    result_args = []

    for arg in args:
        if "=" in arg:
            name, value = arg.split("=")
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
        return ""


@register.tag(name="kwacro")
def do_macro(parser, token):
    try:
        args = token.split_contents()
        macro_name, args = args[1], args[2:]
    except IndexError:
        m = (
            "'%s' tag requires at least one argument (macro name)"
            % token.contents.split()[0]
        )
        raise template.TemplateSyntaxError(m)
    # TODO: could do some validations here,
    # for now, "blow your head clean off"
    nodelist = parser.parse(("endkwacro",))
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
        return ""


@register.tag(name="loadkwacros")
def do_loadmacros(parser, token):
    try:
        tag_name, filename = token.split_contents()
    except IndexError:
        m = (
            "'%s' tag requires at least one argument (macro name)"
            % token.contents.split()[0]
        )
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
                context[name] = FilterExpression(default, self.macro.parser).resolve(
                    context
                )
        return self.macro.nodelist.render(context)


@register.tag(name="usekwacro")
def do_usemacro(parser, token):
    try:
        args = token.split_contents()
        macro_name, values = args[1], args[2:]
    except IndexError:
        m = (
            "'%s' tag requires at least one argument (macro name)"
            % token.contents.split()[0]
        )
        raise template.TemplateSyntaxError(m)
    try:
        macro = parser._macros[macro_name]
    except (AttributeError, KeyError):
        m = "Macro '%s' is not defined" % macro_name
        raise template.TemplateSyntaxError(m)

    fe_args, fe_kwargs = parse_token_args(
        values, lambda value: FilterExpression(value, parser)
    )
    macro.parser = parser
    return UseMacroNode(macro, fe_args, fe_kwargs)
