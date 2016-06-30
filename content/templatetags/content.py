from django import template
from django.utils import formats, html, safestring, text, timezone
import markdown as python_markdown
from markdown.extensions import nl2br
from pymdownx import magiclink

register = template.Library()

@register.filter(needs_autoescape=True)
def markdown(text, autoescape=True):
    if autoescape:
        esc = html.conditional_escape
    else:
        esc = lambda x: x
    return safestring.mark_safe(python_markdown.markdown(esc(text), extensions=[magiclink.MagiclinkExtension(), nl2br.Nl2BrExtension()]))

@register.filter
def permitted(content, user):
    return content.permitted(user)

@register.filter
def preview(events):
    return ', '.join(map(lambda e: '{} {}'.format(formats.time_format(timezone.localtime(e.time)), e.title), events))
