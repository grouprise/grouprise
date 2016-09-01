from .base import View  # NOQA
from .edit import CreateView as Create, FormView as Form  # NOQA
import utils.views


class Delete(utils.views.Delete):
    pass
