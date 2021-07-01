from django.contrib import admin

from . import models

admin.site.register(models.MatrixChatGestaltSettings)
admin.site.register(models.MatrixChatGroupRoom)
admin.site.register(models.MatrixChatGroupRoomInvitations)
