from . import models
from django.contrib.contenttypes import models as contenttypes_models
from utils import views


class Subscribe(views.Create):
    fields = ('content_type', 'object_id', 'subscriber',)
    model = models.Subscription

    def get_initial(self):
        return {
                'content_type': contenttypes_models.ContentType.objects \
                        .get_for_model(self.subscribe_to),
                'object_id': self.subscribe_to.pk,
                'subscriber': self.request.user.gestalt.pk,
                }

    # TODO: move this to base class as well
    #def get_menu(self):
    #    return self.get_parent().get_type_name()

    def get_parent(self):
        return self.subscribe_to

    # TODO: move this to base class (related_object)
    def dispatch(self, request, *args, **kwargs):
        self.subscribe_to = self.get_subscribe_to()
        if not self.subscribe_to:
            raise http.Http404('Zu abonnierendes Objekt nicht gefunden')
        return super().dispatch(request, *args, **kwargs)

    def get_permission_object(self):
        return self.subscribe_to


class ContentSubscribe(Subscribe):
    permission = 'subscriptions.create_content_subscription'

    def get_subscribe_to(self):
        return self.get_content()


'''
class AttentionDelete(utils_views.ActionMixin, utils_views.DeleteView):
    action = 'Keine Benachrichtigungen mehr erhalten'
    layout = layout.HTML('<p>Möchtest Du wirklich keine Benachrichtigungen '
            'für den Beitrag <em>{{ attention.attended_object }}</em> mehr erhalten?</p>')
    permission = 'entities.delete_attention'

    def get_menu(self):
        return self.get_parent().get_type_name()

    def get_object(self):
        if 'content_pk' in self.request.resolver_match.kwargs:
            content = shortcuts.get_object_or_404(content_models.Content, pk=self.request.resolver_match.kwargs['content_pk'])
            return content.attentions.get(attendee=self.request.user.gestalt)

    def get_parent(self):
        return self.object.attended_object



class GroupAttentionCreate(utils_views.ActionMixin, generic.CreateView):
    action = 'Benachrichtigungen erhalten'
    form_class = forms.GroupAttention
    menu = 'group'
    permission = 'entities.create_group_attention'

    def get_initial(self):
        return {'attendee_email': self.request.user.email, 'group': self.get_group().pk}

    def get_parent(self):
        return self.get_group()

    def get_permission_object(self):
        return self.get_group()

class GroupAttentionDelete(utils_views.ActionMixin, utils_views.DeleteView):
    action = 'Keine Benachrichtigungen mehr erhalten'
    layout = layout.HTML('<p>Möchtest Du wirklich keine Benachrichtigungen '
            'für die Gruppe <em>{{ group }}</em> mehr erhalten?</p>')
    menu = 'group'
    model = subscriptions_models.Subscription
    permission = 'entities.delete_group_attention'

    def get_parent(self):
        return self.get_group()
'''
