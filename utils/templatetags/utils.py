from django import apps, template
from django.template import loader
from django.utils import safestring

register = template.Library()

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

@register.simple_tag(takes_context=True)
def include_features(context, template_name):
    result = ''
    for app in apps.apps.get_app_configs():
        try:
            t = loader.get_template('{}/{}'.format(app.label, template_name))
            result += t.render(context)
        except template.TemplateDoesNotExist:
            pass
    return safestring.mark_safe(result)
