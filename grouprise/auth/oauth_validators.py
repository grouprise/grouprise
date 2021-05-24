from oauth2_provider.oauth2_validators import OAuth2Validator


class AccountOAuth2Validator(OAuth2Validator):
    """add account information to oauth responses

    https://django-oauth-toolkit.readthedocs.io/en/latest/oidc.html#adding-claims-to-the-id-token
    """

    def get_additional_claims(self, request):
        return {
            "id": request.user.username,
            "email": request.user.email,
            "display_name": request.user.get_full_name() or request.user.username,
        }
