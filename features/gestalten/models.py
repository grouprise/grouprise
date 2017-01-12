from core import colors
from django.conf import settings
from django.db import models


class Gestalt(models.Model):
    about = models.TextField('Selbstauskunft', blank=True)
    #addressed_content = models.ManyToManyField(
    #        'content.Content', related_name='gestalten', through='entities.GestaltContent')
    avatar = models.ImageField(blank=True)
    avatar_color = models.CharField(max_length=7, default=colors.get_random_color)
    background = models.ImageField('Hintergrundbild', blank=True)
    public = models.BooleanField(
            'Benutzerseite veröffentlichen',
            default=False,
            help_text='Meine Benutzerseite ist für alle Besucherinnen sichtbar.'
            )
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
