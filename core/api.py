from rest_framework import routers

router = routers.DefaultRouter()


def register(callback):
    callback(router)
    return callback
