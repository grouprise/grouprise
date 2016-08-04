from crispy_forms import bootstrap, helper, layout
from django.forms import models as django


class ModelForm(django.ModelForm):
    def __init__(self, **kwargs):
        action = kwargs.pop('action')
        data_fields = kwargs.pop('data_fields')
        description = kwargs.pop('description')
        super().__init__(**kwargs)
        self.data_fields = data_fields
        self.fields.update(self.get_form_fields())
        self.helper = helper.FormHelper()
        self.helper.layout = self.get_layout(
                action=action, description=description)

    def clean(self):
        for field in self.data_fields:
            field.clean(self)
        return super().clean()

    def get_form_fields(self):
        fields = [(f.get_name(), f.get_form_field()) for f in self.data_fields]
        return dict(filter(lambda x: x[0] and x[1], fields))

    def get_layout(self, **kwargs):
        l = [layout.HTML('<p>{}</p>'.format(kwargs['description']))]
        l += filter(None, [f.get_layout() for f in self.data_fields])
        l += [Submit(kwargs['action'])]
        return layout.Layout(*l)

    def save(self, commit=True):
        for field in self.data_fields:
            setattr(self.instance, field.name, field.get_data(
                self.cleaned_data.get(field.get_name())))
        return super().save()


class Submit(bootstrap.StrictButton):
    field_classes = "btn btn-primary"

    def __init__(self, value, name=''):
        super().__init__(value, name=name, value=value, type="submit")
