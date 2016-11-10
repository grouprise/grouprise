from django.db import models


class Conversation(models.Model):
    subject = models.CharField('Thema', max_length=255)
