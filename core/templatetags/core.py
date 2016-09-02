from django import template
from django.conf import settings
from django.contrib.sites import models as sites_models

register = template.Library()


@register.filter
def full_url(path):
    return '{proto}://{domain}{path}'.format(
            proto=settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL,
            domain=sites_models.Site.objects.get_current().domain,
            path=path)


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
