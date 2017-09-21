from django.db import models

import core.models


class Option(core.models.Model):
    poll = models.ForeignKey('content2.Content', related_name='options')

    def __str__(self):
        if hasattr(self, 'simpleoption'):
            return self.simpleoption.__str__()
        elif hasattr(self, 'eventoption'):
            return self.eventoption.__str__()
        return super().__str__()


class SimpleOption(Option):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class EventOption(Option):
    time = models.DateTimeField()
    until_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.time)


class Vote(core.models.Model):
    class Meta:
        unique_together = (('option', 'voter'), ('option', 'anonymous'))

    option = models.ForeignKey('Option')

    voter = models.ForeignKey('gestalten.Gestalt', null=True, related_name='votes')
    anonymous = models.CharField(max_length=63, blank=True, null=True)

    time_updated = models.DateTimeField(auto_now=True)

    endorse = models.BooleanField(default=False)
