import utils.forms
import utils.views


class Field(utils.forms.Field):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.data = kwargs.get('data', None)
        self.name = name


class Create(utils.views.Create):
    def get_initial(self):
        initial = super().get_initial()
        for field in self._fields:
            if field.data == 'actor':
                initial[field.name] = self.request.user.gestalt.pk
        return initial


class Delete(utils.views.Delete):
    pass
