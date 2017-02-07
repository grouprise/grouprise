import bleach as python_bleach
from django import template
from django.utils import formats, html, safestring, timezone
from django.template.base import FilterExpression
from django.template.defaultfilters import truncatewords_html, truncatewords
from django.template.loader import get_template
import markdown as python_markdown
from markdown.extensions import nl2br, toc, sane_lists, fenced_code
from pymdownx import magiclink
from mdx_unimoji import UnimojiExtension
import utils.markdown

register = template.Library()

markdown_extensions = (
    magiclink.MagiclinkExtension(),
    nl2br.Nl2BrExtension(),
    utils.markdown.GroupReferenceExtension(),
    sane_lists.SaneListExtension(),
    fenced_code.FencedCodeExtension(),
    utils.markdown.CuddledListExtension(),
    UnimojiExtension()
)

content_allowed_tags = (
    # text
    'p', 'em', 'strong', 'br', 'a', 'img',
    # citation
    'blockquote', 'cite',
    # headings
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    # lists
    'ol', 'ul', 'li',
    # code
    'pre', 'code'
)

content_allowed_attributes = {
    '*': 'title',
    'a': ['href'],
    'code': ['class'],
    'img': ['src', 'alt']
}


@register.filter
def bleach(text, disable_tags=tuple()):
    if disable_tags == "all":
        allowed_tags = tuple()
    else:
        allowed_tags = set(content_allowed_tags) - set(disable_tags)
    bleached = python_bleach.clean(
            text, strip=True, tags=allowed_tags, attributes=content_allowed_attributes)
    if isinstance(text, safestring.SafeString):
        return safestring.mark_safe(bleached)
    else:
        return bleached


@register.filter(needs_autoescape=True)
def markdown(text, autoescape=True):
    return safestring.mark_safe(python_markdown.markdown(
        html.conditional_escape(text) if autoescape else text, extensions=markdown_extensions))


@register.simple_tag(name="markdown")
def markdown_tag(
        text, heading_baselevel=1, filter_tags=True, truncate=False, disable_tags="",
        plain_preview=False):
    extensions = markdown_extensions + (toc.TocExtension(baselevel=heading_baselevel), )
    result = python_markdown.markdown(text, extensions=extensions)
    if filter_tags:
        disabled_tags = tuple(disable_tags.split(","))
        result = bleach(result, disabled_tags)
    if truncate:
        result = truncatewords_html(result, truncate)
    if plain_preview:
        result = bleach(result, disable_tags="all")
        result = truncatewords(result, plain_preview)
        result = html.conditional_escape(result)

    return safestring.mark_safe(result)


@register.filter
def permitted(content, user):
    return content.permitted(user)


@register.filter
def preview(events):
    return ', '.join([
        '{} {}'.format(formats.time_format(timezone.localtime(e.time)), e.title)
        for e in events])


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
        self.args = []
        self.kwargs = {}
        for a in args:
            if "=" not in a:
                self.args.append(a)
            else:
                name, value = a.split("=")
                self.kwargs[name] = value

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

    fe_kwargs = {}
    fe_args = []

    for val in values:
        if "=" in val:
            # kwarg
            name, value = val.split("=")
            fe_kwargs[name] = FilterExpression(value, parser)
        else:  # arg
            # no validation, go for it ...
            fe_args.append(FilterExpression(val, parser))

    macro.parser = parser
    return UseMacroNode(macro, fe_args, fe_kwargs)
