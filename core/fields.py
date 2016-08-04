from django import forms
import functools


class Field:
    def __init__(self, view):
        self.view = view

    def get_form_field(self):
        return None

    def get_layout(self):
        return None

    def get_model_form_field(self):
        return None


def fieldclass_factory(superclass, name):
    classname = name.replace('_', '').capitalize() + superclass.__name__
    return type(classname, (superclass,), {'name': name})


class CurrentGestalt(Field):
    def get_data(self, form_data):
        if self.view.request.user.is_authenticated():
            return self.view.request.user.gestalt
        else:
            raise 'Gestalt anlegen!'

    def get_form_field(self):
        if not self.view.request.user.is_authenticated():
            return (self.name, forms.EmailField(label='E-Mail-Adresse'))
        return None

    def get_layout(self):
        return self.name

current_gestalt = functools.partial(fieldclass_factory, CurrentGestalt)


class RelatedObject(Field):
    def get_data(self, form_data):
        return self.view.related_object

related_object = functools.partial(fieldclass_factory, RelatedObject)
