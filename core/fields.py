class Field:
    def __init__(self, view):
        self.view = view


def fieldclass_factory(superclass, name):
    classname = name.replace('_', '').capitalize() + superclass.__name__
    return type(classname, (superclass,), {'name': name})


class CurrentGestalt(Field):
    def get_data(self):
        return self.view.request.user.gestalt


def current_gestalt(name):
    return fieldclass_factory(CurrentGestalt, name)


class RelatedObject(Field):
    def get_data(self):
        return self.view.related_object


def related_object(name):
    return fieldclass_factory(RelatedObject, name)
