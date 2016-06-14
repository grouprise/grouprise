from . import forms, models
from django.core import urlresolvers
from django.views import generic
from utils import forms as utils_forms, views as utils_views


class BaseContent(utils_views.ActionMixin, generic.CreateView):
    permission = 'content.create_content'

    def get_back_url(self):
        if self.get_group():
            return self.get_group().get_absolute_url()
        else:
            return urlresolvers.reverse(self.back_url)

    def get_initial(self):
        return {'author': self.request.user.gestalt.pk, 'group': self.get_group(), 'pinned': self.request.GET.get('pinned'), 'public': self.request.GET.get('public')}

    def get_permission_object(self):
        return None


class Article(BaseContent):
    action = 'Artikel erstellen'
    back_url = 'article-index'
    form_class = forms.Article
    menu = 'article'


class Event(BaseContent):
    action = 'Ereignis erstellen'
    back_url = 'event-index'
    form_class = forms.Event
    menu = 'event'


class Gallery(BaseContent):
    action = 'Galerie erstellen'
    back_url = 'gallery-index'
    form_class = forms.Gallery
    menu = 'gallery'


class BaseMessage(utils_views.ActionMixin, generic.CreateView):
    action = 'Nachricht senden'
    message = 'Die Nachricht wurde versendet.'

    def get_initial(self):
        return {'recipient': self.get_recipient().pk, 'sender': self.request.user.email}

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


class CommentCreate(utils_views.ActionMixin, generic.CreateView):
    #action = 'Kommentieren'
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
    action = 'Bild hinzufügen'
    fields = ('file',)
    layout = 'file'
    model = models.Image
    permission = 'content.create_image'

    def form_valid(self, form):
        form.instance.content = self.get_permission_object()
        # FIXME: race condition
        form.instance.weight = form.instance.content.images.last().weight + 1 if form.instance.content.images.exists() else 0
        return super().form_valid(form)

    def get_menu(self):
        return self.get_parent().get_type_name()

    def get_parent(self):
        pk = self.request.resolver_match.kwargs['content_pk']
        return models.Content.objects.get(pk=pk)

    def get_permission_object(self):
        return self.get_parent()
