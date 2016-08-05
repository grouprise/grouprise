from django import apps, template
from django.core import urlresolvers
from django.utils import safestring

register = template.Library()

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
