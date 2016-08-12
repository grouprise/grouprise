from . import actions
import utils.views


class Create(actions.TemplateResponseMixin, actions.BaseCreateView):
    pass


class Delete(utils.views.Delete):
    pass
