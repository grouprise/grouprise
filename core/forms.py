from django.forms import models as django


class ModelForm(django.ModelForm):
    def __init__(self, **kwargs):
        self.data_fields = kwargs.pop('data_fields')
        super().__init__(**kwargs)

    def save(self, commit=True):
        for field in self.data_fields:
            setattr(self.instance, field.name, field.get_data())
        return super().save()
