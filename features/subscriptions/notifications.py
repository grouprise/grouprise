from features.content import notifications as content
from features.gestalten import models as gestalten


class ContentPublicallyAssociated(content.ContentAssociated):
    def get_recipients(self):
        return gestalten.Gestalt.objects.filter(
                subscriptions__content_type=self.object.entity_type,
                subscriptions__object_id=self.object.entity_id,
                subscriptions__unsubscribe=False)

    def get_sender(self):
        return None
