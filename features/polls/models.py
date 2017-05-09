from django.db import models

import core.models


class Option(core.models.Model):
    class Meta:
        ordering = ('id',)

    poll = models.ForeignKey('content2.Content', related_name='options')
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Vote(core.models.Model):
    class Meta:
        ordering = ('option__id',)

    option = models.ForeignKey('Option')

    voter = models.ForeignKey('gestalten.Gestalt', null=True)
    anonymous = models.CharField(max_length=63, blank=True)

    endorse = models.BooleanField(default=False)
