from . import forms, models
from django.conf import settings
from django.core import urlresolvers
from django.views import generic
from features.groups import models as groups
from utils import forms as utils_forms, views as utils_views


class BaseContent(utils_views.ActionMixin, generic.CreateView):
    permission = 'content.create_content'

    def get_initial(self):
        return {
                'author': self.request.user.gestalt.pk,
                'group': self.get_group(),
                'pinned': self.request.GET.get('pinned'),
                'public': self.request.GET.get('public')}

    def get_permission_object(self):
        return None


class Article(BaseContent):
    action = 'Artikel erstellen'
    form_class = forms.Article
    menu = 'article'
    parent = 'article-index'


class Event(BaseContent):
    action = 'Ereignis erstellen'
    form_class = forms.Event
    menu = 'event'
    parent = 'event-index'


class Gallery(BaseContent):
    action = 'Galerie erstellen'
    form_class = forms.Gallery
    menu = 'gallery'
    parent = 'gallery-index'


class BaseMessage(utils_views.ActionMixin, generic.CreateView):
    action = 'Nachricht senden'
    message = 'Die Nachricht wurde versendet.'

    def get_initial(self):
        if self.request.user.is_authenticated():
            return {'recipient': self.get_recipient().pk, 'sender': self.request.user.email}
        else:
            return {'recipient': self.get_recipient().pk}

    def get_parent(self):
        return self.get_recipient()

    def get_permission_object(self):
        return self.get_recipient()


class GestaltMessage(BaseMessage):
    form_class = forms.GestaltMessage
    menu = 'gestalt'
    permission = 'entities.create_gestalt_message'

    def get_recipient(self):
        return self.get_gestalt()


class GroupMessage(BaseMessage):
    form_class = forms.GroupMessage
    menu = 'group'
    permission = 'entities.create_group_message'

    def get_recipient(self):
        return self.get_group()


class AbuseMessage(GroupMessage):
    action = 'Missbrauch melden'

    def get_initial(self):
        initial = super().get_initial()
        initial['text'] = ('{}\n\nIch bin der Ansicht, dass der Inhalt dieser Seite gegen '
                           'Regeln verstößt.'.format(
                               self.request.build_absolute_uri(self.kwargs['path'])))
        initial['title'] = 'Missbrauch melden'
        return initial

    def get_recipient(self):
        return groups.Group.objects.get(id=settings.ABOUT_GROUP_ID)


class CommentCreate(utils_views.ActionMixin, generic.CreateView):
    # FIXME: action = 'Kommentieren'
    fields = ('text',)
    layout = utils_forms.EditorField('text')
    model = models.Comment
    permission = 'content.create_comment'

    def get_action(self):
        return 'Kommentieren' if self.get_parent().public else 'Antworten'

    def form_valid(self, form):
        form.instance.author = self.request.user.gestalt
        form.instance.content = self.get_permission_object()
        return super().form_valid(form)

    def get_helper(self):
        helper = super().get_helper()
        helper.form_action = urlresolvers.reverse('comment-create', args=[self.get_parent().pk])
        return helper

    def get_menu(self):
        return self.get_parent().get_type_name()

    def get_parent(self):
        return models.Content.objects.get(pk=self.kwargs['content_pk'])

    def get_permission_object(self):
        return self.get_parent()


class ImageCreate(utils_views.ActionMixin, generic.CreateView):
    action = 'Bilder hinzufügen'
    fields = ('file',)
    layout = 'file'
    model = models.Image
    permission = 'content.create_image'

    def form_valid(self, form):
        form.instance.content = self.get_permission_object()
        return super().form_valid(form)

    def get_menu(self):
        return self.get_parent().get_type_name()

    def get_pk(self):
        return int(self.request.resolver_match.kwargs['content_pk'])

    def get_parent(self):
        return models.Content.objects.get(pk=self.get_pk())

    def get_helper(self):
        import json
        helper = super().get_helper()
        helper.attrs['data-component'] = 'image-upload'
        helper.attrs['data-component-conf'] = json.dumps({'content': self.get_pk()})
        return helper

    def get_template_names(self):
        return 'stadt/form_image.html'

    def get_permission_object(self):
        return self.get_parent()
