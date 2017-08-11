from crispy_forms import bootstrap, helper, layout
from django import forms as django


class GroupSelect(django.Select):
    template_name = 'core/widgets/group_select.html'


class EditorTextarea(django.Textarea):
    has_buttons = True

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['editor'] = True
        return context


class StadtMixin:
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
        return dict(filter(lambda x: x[1], fields))

    def get_layout(self, **kwargs):
        l = []
        if kwargs['description']:
            l += [layout.HTML('<p>{}</p>'.format(kwargs['description']))]
        l += filter(None, [f.get_layout() for f in self.data_fields])
        l += [Submit(kwargs['action'])]
        return layout.Layout(*l)


class Form(StadtMixin, django.Form):
    pass


class ModelForm(StadtMixin, django.ModelForm):
    def save(self, commit=True):
        for field in self.data_fields:
            field.save_data(self)
        obj = super().save()
        for field in self.data_fields:
            field.save_references(obj)
        return obj


class Submit(bootstrap.StrictButton):
    field_classes = "btn btn-primary"

    def __init__(self, value, name=''):
        super().__init__(value, name=name, value=value, type="submit")
