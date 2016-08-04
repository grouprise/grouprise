from crispy_forms import helper
from django.forms import models as django


class ModelForm(django.ModelForm):
    def __init__(self, **kwargs):
        self.data_fields = kwargs.pop('data_fields')
        super().__init__(**kwargs)
        self.helper = helper.FormHelper()
        for data_field in self.data_fields:
            form_field = data_field.get_form_field()
            if form_field:
                self.fields[form_field[0]] = form_field[1]

    def save(self, commit=True):
        for field in self.data_fields:
            setattr(self.instance, field.name, field.get_data(
                self.cleaned_data.get(field.name)))
        return super().save()
