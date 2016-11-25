from .base import View  # NOQA
from .edit import CreateView as Create, FormView as Form  # NOQA
from .list import ListView as List
import utils.views


class Delete(utils.views.Delete):
    pass
