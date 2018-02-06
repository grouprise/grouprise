from django.apps import AppConfig
from watson import search as watson

class AssociationsConfig(AppConfig):
    name = "features.associations"

    def ready(self):
        watson.register(
                self.get_model("Association").objects.exclude_deleted().filter(public=True),
                fields=(
                    'content__title',
                    'content__place',
                    'content__versions__text',
                    #'content__taggeds__tag__name',
                    'content__contributions__contribution__text',
                ))
