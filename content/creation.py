from . import forms, models
from django.views import generic
from utils import views as util_views

class Article(util_views.ActionMixin, generic.CreateView):
    action = 'Artikel erstellen'
    back_url = 'article-index'
    form_class = forms.Article
    menu = 'article'
    model = models.Article
    permission = 'entities.create_gestalt_content'

    def get_initial(self):
        return {'author': self.request.user.gestalt.pk}

    def get_permission_object(self):
        return self.get_gestalt()

class BaseMessageCreate(util_views.ActionMixin, generic.CreateView):
    action = 'Nachricht senden'
    message = 'Die Nachricht wurde versendet.'
    model = models.Article

    def get_initial(self):
        return {'recipient': self.get_recipient().pk, 'sender': self.request.user.email}

    def get_parent(self):
        return self.get_recipient()

    def get_permission_object(self):
        return self.get_recipient()

class GestaltMessageCreate(BaseMessageCreate):
    form_class = forms.GestaltMessage
    menu = 'gestalt'
    permission = 'entities.create_gestalt_message'

    def get_recipient(self):
        return self.get_gestalt()

class GroupMessageCreate(BaseMessageCreate):
    form_class = forms.GroupMessage
    menu = 'group'
    permission = 'entities.create_group_message'

    def get_recipient(self):
        return self.get_group()
