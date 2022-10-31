from oauth2_provider.oauth2_validators import OAuth2Validator


class AccountOAuth2Validator(OAuth2Validator):
    """add account information to oauth responses

    https://django-oauth-toolkit.readthedocs.io/en/latest/oidc.html#adding-claims-to-the-id-token

    Claims and scopes:
    - "claims" are account attributes, which the server may share with an OIDC client
    - the OIDC client application (e.g. the matrix server) requests a configured set of scopes
      (e.g. "openid", "email" and "profile")
    - the available set of data (published by grouprise) is defined in `get_additional_claims`
    - the actually returned set of data is limited to the keys belonging to the requested scopes
      (with `oidc_claim_scope` mapping claims to scopes)
    """

    # TODO: access the attribute directly, as soon as we require django-oauth-toolkit >= 2.0
    oidc_claim_scope = getattr(OAuth2Validator, "oidc_claim_scope", {}) | {
        "display_name": "profile",
        "email": "email",
        "id": "profile",
    }

    def get_additional_claims(self, request):
        return {
            "id": request.user.username,
            "email": request.user.email,
            "display_name": request.user.get_full_name() or request.user.username,
        }
