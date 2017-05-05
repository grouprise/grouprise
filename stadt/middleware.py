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

import sys

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.views.debug import ExceptionReporter
from django.core import mail


class DoesNotExistMiddleware:
    def process_exception(self, request, exception):
        if isinstance(exception, ObjectDoesNotExist):
            exc_info = sys.exc_info()
            reporter = ExceptionReporter(request, is_email=True, *exc_info)
            subject = "[Django] Page not found %s" % request.path
            message = "%s\n\n%s" % (
                reporter.get_traceback_text(),
                repr(request)
            )
            mail.mail_admins(
                subject, message, fail_silently=True,
                html_message=reporter.get_traceback_html()
            )
            raise Http404 from exception
