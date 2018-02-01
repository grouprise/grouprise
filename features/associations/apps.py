from django.apps import AppConfig
from watson import search as watson

class AssociationsConfig(AppConfig):
    name = "features.associations"

    def ready(self):
        watson.register(self.get_model("Association"), fields=('content__title',))
