from .base import View
from .edit import CreateView as Create, FormView as Form
import utils.views


class Delete(utils.views.Delete):
    pass
