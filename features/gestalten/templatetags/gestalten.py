import django

register = django.template.Library()


@register.simple_tag(takes_context=True)
def login_url(context):
    # FIXME: can we use mark_safe here? what about url encoding?
    return django.utils.safestring.mark_safe('{}?next={}'.format(
        django.core.urlresolvers.reverse('account_login'), context['request'].path))
