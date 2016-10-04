from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404


class DoesNotExistMiddleware:
    def process_exception(self, request, exception):
        if isinstance(exception, ObjectDoesNotExist):
            raise Http404 from exception
