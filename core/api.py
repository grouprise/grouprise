from rest_framework import routers

# router for frontend api
router = routers.DefaultRouter()

# router for transition connect api
tc_router = routers.SimpleRouter()


def register(callback):
    callback(router)
    return callback


def register_tc(callback):
    callback(tc_router)
    return callback
