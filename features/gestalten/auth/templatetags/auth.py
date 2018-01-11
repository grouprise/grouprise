import django

register = django.template.Library()


@register.simple_tag(takes_context=True)
def login_or_field(context, field):
    return django.utils.safestring.mark_safe(
            '<a href="{}">Anmelden</a> oder {} angeben'.format(login_url(context), field.label))


@register.simple_tag(takes_context=True)
def login_url(context):
    return django.utils.safestring.mark_safe('{}?{}'.format(
        django.urls.reverse('login'),
        django.utils.http.urlencode({'next': context['request'].path})))
