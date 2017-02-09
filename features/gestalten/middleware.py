from core.views import app_config


class GestaltAppConfigMiddleware:
    def process_request(self, request):
        try:
            gestalt_id = request.user.gestalt.id
        except AttributeError:
            gestalt_id = None

        app_config.add_setting('gestalt', {
            'id': gestalt_id
        })
