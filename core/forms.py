# Use with care. See
# https://git.hack-hro.de/stadtgestalten/stadtgestalten/issues/468

from crispy_forms import bootstrap, helper, layout
from django import forms as django
from simplemathcaptcha.fields import MathCaptchaField, MathCaptchaWidget


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
        lay = []
        if kwargs['description']:
            lay += [layout.HTML('<p>{}</p>'.format(kwargs['description']))]
        lay += filter(None, [f.get_layout() for f in self.data_fields])
        lay += [Submit(kwargs['action'])]
        return layout.Layout(*lay)


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

    def __init__(self, value, name='', field_classes=None):
        if field_classes is not None:
            self.field_classes = field_classes
        super().__init__(value, name=name, value=value, type="submit")


class LayoutMixin:
    def get_helper(self):
        h = helper.FormHelper()
        h.layout = layout.Layout(*self.get_layout())
        if hasattr(self, 'inline') and self.inline:
            h.field_template = 'bootstrap3/layout/inline_field.html'
            h.form_class = 'form-inline'
        if hasattr(self, 'search') and self.search:
            h.field_template = 'bootstrap3/layout/inline_field.html'
            h.form_class = 'form-search'
        return h

    def get_layout(self):
        layout = self.layout if hasattr(self, 'layout') else tuple()
        if not isinstance(layout, (tuple, list)):
            layout = (layout,)
        return layout


class FormMixin(LayoutMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.get_helper()
        if hasattr(self, 'method'):
            self.helper.form_method = self.method


class ExtraFormMixin(FormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        kwargs['instance'] = self.get_instance()
        self.extra_form = self.extra_form_class(*args, **kwargs)
        self.errors.update(self.extra_form.errors)
        self.fields.update(self.extra_form.fields)
        self.initial.update(self.extra_form.initial)

    def is_valid(self):
        return super().is_valid() and self.extra_form.is_valid()

    def save(self, commit=True):
        self.extra_form.save()
        return super().save(commit)


class EditorField(layout.Field):
    def __init__(self, *args, **kwargs):
        kwargs['data_component'] = 'editor'
        super().__init__(*args, **kwargs)


class Field(layout.Field):
    def __init__(self, name, **kwargs):
        self.constant = False
        if 'type' in kwargs and kwargs['type'] == 'constant':
            self.constant = True
            kwargs['type'] = 'hidden'
        super().__init__(name, **kwargs)


class Captcha(MathCaptchaField):
    class Widget(MathCaptchaWidget):
        def get_context(self, *args, **kwargs):
            ctx = super().get_context(*args, **kwargs)
            ctx['label_id'] = ctx['widget']['subwidgets'][0]['attrs']['id']
            return ctx

    default_error_messages = {
        'invalid': 'Knapp daneben! Probiere es noch einmal!',
        'invalid_number': 'Bitte gib nur einfache Ziffern ein.',
    }

    def __init__(self, *args, **kwargs):
        widget = self.Widget(question_tmpl='Was ergibt %(num1)i %(operator)s %(num2)i?')
        kwargs.setdefault('widget', widget)
        super().__init__(*args, **kwargs)

    def get_bound_field(self, *args, **kwargs):
        field = super().get_bound_field(*args, **kwargs)
        field.label = None
        return field
