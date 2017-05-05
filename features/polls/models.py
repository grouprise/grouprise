from django.db import models

import core.models


class Option(core.models.Model):
    poll = models.ForeignKey('content2.Content')
    title = models.CharField(max_length=255)


class Vote(core.models.Model):
    option = models.ForeignKey('Option')
    
    voter = models.ForeignKey('gestalten.Gestalt', null=True)
    anonymous = models.CharField(max_length=63, blank=True)

    endorse = models.BooleanField()
