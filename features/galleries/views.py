"""
This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.
"""

import features.content.views
from . import forms


class Create(features.content.views.Create):
    template_name = 'galleries/create.html'

    form_class = forms.Create

    def get_initial(self):
        initial = super().get_initial()
        initial['title'] = self.request.GET.get('title', initial.get('title'))
        initial['text'] = self.request.GET.get('text', initial.get('text'))
        initial['pinned'] = self.request.GET.get('pinned', initial.get('pinned'))
        initial['public'] = self.request.GET.get('public', initial.get('public'))
        return initial
