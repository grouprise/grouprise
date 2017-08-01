import django


class Markdown(django.views.generic.TemplateView):
    template_name = 'core/markdown.html'
