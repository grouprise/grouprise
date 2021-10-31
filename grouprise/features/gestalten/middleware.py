from grouprise.core.views import app_config


class GestaltAppConfigMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            gestalt_id = request.user.gestalt.id
        except AttributeError:
            gestalt_id = None

        app_config.add_setting("gestalt", {"id": gestalt_id})

        return self.get_response(request)
