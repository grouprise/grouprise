from django import forms
from entities import models as entities_models
import functools


def fieldclass_factory(superclass, name, **kwargs):
    classname = name.replace('_', '').capitalize() + superclass.__name__
    kwargs['name'] = name
    return type(classname, (superclass,), kwargs)


class Field:
    has_data = False

    def __init__(self, view):
        self.view = view

    def clean(self, form):
        pass

    def get_data(self, form_data):
        return form_data

    def get_form_field(self):
        return None

    def get_layout(self):
        return self.get_name()

    def get_model_form_field(self):
        return None

    def get_name(self):
        return self.name

    def save_data(self, form):
        if self.has_data:
            setattr(form.instance, self.name, self.get_data(
                form.cleaned_data.get(self.get_name())))

field = functools.partial(fieldclass_factory, Field)


class ModelField(Field):
    def get_model_form_field(self):
        return self.name

model_field = functools.partial(fieldclass_factory, ModelField)


class Constant(Field):
    has_data = True

    def get_data(self, form_data):
        return self.value

constant = functools.partial(fieldclass_factory, Constant)


class Email(Field):
    def get_form_field(self):
        return forms.EmailField(label='E-Mail-Adresse')

    def get_name(self):
        return '{}_email'.format(self.name)

email = functools.partial(fieldclass_factory, Email)


class EmailGestalt(Email):
    has_data = True

    def get_data(self, form_data):
        return entities_models.Gestalt.get_or_create(form_data)

email_gestalt = functools.partial(fieldclass_factory, EmailGestalt)


class CurrentGestalt(Field):
    has_data = True
    null = False

    def clean(self, form):
        if not self.view.request.user.is_authenticated() and not self.null:
            try:
                gestalt = entities_models.Gestalt.objects.get(
                        user__email=form.cleaned_data.get(self.get_name()))
                if gestalt.can_login():
                    form.add_error(self.get_name(), forms.ValidationError(
                        'Es gibt bereits ein Benutzerkonto mit dieser '
                        'E-Mail-Adresse. Bitte melde Dich mit E-Mail-Adresse '
                        'und Kennwort an.', code='existing'))
            except entities_models.Gestalt.DoesNotExist:
                pass

    def get_data(self, form_data):
        if self.view.request.user.is_authenticated():
            return self.view.request.user.gestalt
        elif not self.null:
            return entities_models.Gestalt.get_or_create(form_data)
        else:
            return None

    def get_form_field(self):
        if not self.view.request.user.is_authenticated() and not self.null:
            return forms.EmailField(label='E-Mail-Adresse')
        return None

    def get_layout(self):
        if not self.view.request.user.is_authenticated() and not self.null:
            return super().get_layout()
        return None

    def get_name(self):
        return '{}_email'.format(self.name)

current_gestalt = functools.partial(fieldclass_factory, CurrentGestalt)


class ViewObject(Field):
    has_data = True

    def get_data(self, form_data):
        return self.view.get_view_object(self.key)

    def get_layout(self):
        return None

view_object = functools.partial(fieldclass_factory, ViewObject)


class RelatedObject(ViewObject):
    has_data = True

    def get_data(self, form_data):
        return self.view.related_object

related_object = functools.partial(fieldclass_factory, RelatedObject)


class CreateReference(Field):
    def save_data(self, form):
        ref = getattr(form.instance, self.name)
        ref.objects.create(**self.kwargs)

create_reference = functools.partial(fieldclass_factory, CreateReference)
