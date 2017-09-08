from django.db import models


class Note(models.Model):
    related_to = models.ForeignKey('associations.Association', on_delete=models.CASCADE)
    text = models.CharField(max_length=70)
    time_created = models.DateTimeField(auto_now_add=True)
    gestalt_created = models.ForeignKey(
            'gestalten.Gestalt', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.text
