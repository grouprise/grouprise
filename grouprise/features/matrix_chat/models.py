from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from grouprise.features.matrix_chat.settings import MATRIX_SETTINGS


class MatrixChatGroupRoom(models.Model):

    group = models.ForeignKey(
        "groups.Group", related_name="matrix_rooms", on_delete=models.CASCADE
    )
    room_id = models.CharField(max_length=256)
    is_private = models.BooleanField()

    def get_client_url(self):
        return f"/stadt/chat/#/room/{self.room_id}"

    def __str__(self):
        if self.is_private:
            return "MatrixChatGroupRoom<{}, private, {}>".format(
                self.group.name, self.room_id
            )
        else:
            return "MatrixChatGroupRoom<{}, public, {}>".format(
                self.group.name, self.room_id
            )


class MatrixChatGroupRoomInvitations(models.Model):

    room = models.ForeignKey(
        "matrix_chat.MatrixChatGroupRoom",
        related_name="invitations",
        on_delete=models.CASCADE,
    )
    time_invited = models.DateTimeField(auto_now=True)
    gestalt = models.ForeignKey(
        "gestalten.Gestalt", related_name="+", on_delete=models.CASCADE
    )


class MatrixChatGestaltSettings(models.Model):

    matrix_id_override = models.CharField(max_length=256, blank=True)
    gestalt = models.OneToOneField(
        "gestalten.Gestalt",
        related_name="matrix_chat_settings",
        on_delete=models.CASCADE,
    )

    @staticmethod
    def get_default_local_matrix_id(gestalt):
        return "@{}:{}".format(gestalt.slug, MATRIX_SETTINGS.DOMAIN)

    @classmethod
    def get_matrix_id(cls, gestalt):
        try:
            return gestalt.matrix_chat_settings.matrix_id_override
        except ObjectDoesNotExist:
            return cls.get_default_local_matrix_id(gestalt)

    @property
    def matrix_id(self):
        if self.matrix_id_override:
            return self.matrix_id_override
        else:
            return self.get_default_local_matrix_id(self.gestalt)

    def __str__(self):
        return self.matrix_id
