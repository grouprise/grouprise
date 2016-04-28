from . import forms, models
from django.core import urlresolvers
from django.views import generic
from utils import views as utils_views


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
