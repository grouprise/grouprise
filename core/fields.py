class Field:
    def __init__(self, name):
        self.name = name


class CurrentGestalt(Field):
    def get_data(self):
        return self.view.request.user.gestalt


class RelatedObject(Field):
    def get_data(self):
        return self.view.related_object
