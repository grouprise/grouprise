import markdown as python_markdown
from django import template
from django.utils import html, safestring

register = template.Library()

@register.filter(needs_autoescape=True)
def markdown(text, autoescape=True):
    if autoescape:
        esc = html.conditional_escape
    else:
        esc = lambda x: x
    return safestring.mark_safe(python_markdown.markdown(esc(text)))

@register.filter
def permitted(content, user):
    return content.permitted(user)
