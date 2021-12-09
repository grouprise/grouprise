import json

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from grouprise.features.matrix_chat.settings import MATRIX_SETTINGS


class MatrixChatGroupRoom(models.Model):

    group = models.ForeignKey(
        "groups.Group", related_name="matrix_rooms", on_delete=models.CASCADE
    )
    room_id = models.CharField(max_length=256)
    is_private = models.BooleanField()
    is_visible = models.BooleanField(default=True)
    statistics_cache_json = models.CharField(default="{}", max_length=4096)

    def get_statistics(self):
        try:
            return json.loads(self.statistics_cache_json)
        except ValueError:
            return {}

    def set_statistics(self, data):
        self.statistics_cache_json = json.dumps(data)

    @property
    def members_count(self):
        return self.get_statistics().get("members_count", 0)

    def get_default_room_alias(self):
        group_slug = self.group.slug or self.group.name
        name_suffix = "-private" if self.is_private else ""
        return f"#{group_slug}{name_suffix}:{MATRIX_SETTINGS.DOMAIN}"

    def __str__(self):
        if self.is_private:
            return "{} (private, {})".format(self.group.name, self.room_id)
        else:
            return "{} (public, {})".format(self.group.name, self.room_id)


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

    def __str__(self):
        return f"{self.gestalt} invited into {self.room}"


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
            matrix_id = gestalt.matrix_chat_settings.matrix_id_override
        except ObjectDoesNotExist:
            matrix_id = None
        if matrix_id:
            return matrix_id
        else:
            return cls.get_default_local_matrix_id(gestalt)

    @property
    def matrix_id(self):
        if self.matrix_id_override:
            return self.matrix_id_override
        else:
            return self.get_default_local_matrix_id(self.gestalt)

    def __str__(self):
        return self.matrix_id
