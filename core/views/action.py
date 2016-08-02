from django.views.generic import edit as django


class DjangoFieldsMixin:
    fields = None

    def __init__(self, *args, **kwargs):
        self.fields = self.get_django_fields()
        super().__init__(*args, **kwargs)

    def get_django_fields(self):
        return self.fields


class ModelFormMixin(DjangoFieldsMixin, django.ModelFormMixin):
    def __init__(self, *args, **kwargs):
        self.stadt_fields = self.get_fields()
        super().__init__(*args, **kwargs)

    def get_django_fields(self):
        return []

    def get_fields(self):
        return self.fields
