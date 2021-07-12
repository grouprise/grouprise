from django.conf import settings

from grouprise.core.settings import LazySettingsResolver, get_grouprise_site


try:
    _MATRIX_SETTINGS = settings.GROUPRISE["MATRIX_CHAT"]
except (KeyError, AttributeError):
    _MATRIX_SETTINGS = {}


MATRIX_SETTINGS = LazySettingsResolver(
    ENABLED=_MATRIX_SETTINGS.get("ENABLED", False),
    DOMAIN=_MATRIX_SETTINGS.get("DOMAIN", lambda: get_grouprise_site().domain),
    ADMIN_API_URL=_MATRIX_SETTINGS.get("ADMIN_API_URL", "http://localhost:8008"),
    BOT_USERNAME=_MATRIX_SETTINGS.get("BOT_USERNAME", "grouprise-bot"),
    BOT_ACCESS_TOKEN=_MATRIX_SETTINGS.get("BOT_ACCESS_TOKEN", None),
)


def get_or_create_oidc_client_application():
    from oauth2_provider.models import Application

    app, created = Application.objects.get_or_create(name="matrix_chat")
    if created:
        app.redirect_uris = (
            f"https://{MATRIX_SETTINGS.DOMAIN}/_synapse/client/oidc/callback"
        )
        app.client_type = "confidential"
        app.authorization_grant_type = "authorization-code"
        app.skip_authorization = True
        app.algorithm = "RS256"
        app.save()
    return app
