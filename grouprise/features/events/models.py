from django.db import models
from django.utils.translation import gettext_lazy as _


class AttendanceStatement(models.Model):
    """ users may connect themselves to Content (e.g. announce to participate in an event) """

    content = models.ForeignKey('content2.Content', on_delete=models.CASCADE,
                                related_name='attendance_statements')
    attendee = models.ForeignKey('gestalten.Gestalt', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True, verbose_name=_("Last Update"))
