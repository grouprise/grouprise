"""
Copyright 2016-2017 sense.lab e.V. <info@senselab.org>

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

from rest_framework import permissions, viewsets
from rest_framework.response import Response
from core.templatetags import core
from core import api

_PRESETS = {
    'content': {
        'heading_baselevel': 2,
    },
}


class MarkdownView(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        preset = _PRESETS[request.data.get('preset', 'content')]
        text = request.data.get('content')
        return Response({
            'content': str(core.markdown(text, **preset))
        })


@api.register
def load(router):
    router.register(r'content/markdown', MarkdownView, base_name='markdown')
