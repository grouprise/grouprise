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
