import django.contrib
from rest_framework import exceptions
from rest_framework.authentication import BasicAuthentication

from grouprise.core.models import PermissionToken


class PermissionTokenUserResolver:

    def __init__(self, feature_key):
        self.feature_key = feature_key

    def _parse_permission_token_from_request(self, request):
        """ retrieve a permission token (if it was supplied) from the query arguments
        """
        query_args = request.GET.copy()
        try:
            full_token = query_args['token']
        except KeyError:
            return None
        try:
            token_username, secret_key = full_token.split(":", 1)
        except ValueError:
            return None
        user_model = django.contrib.auth.get_user_model()
        try:
            user = user_model.objects.get(username=token_username)
        except user_model.DoesNotExist:
            return None
        if user.username == token_username:
            try:
                return PermissionToken.objects.get(secret_key=secret_key, gestalt=user.gestalt,
                                                   feature_key=self.feature_key)
            except PermissionToken.DoesNotExist:
                return None
        return None

    def resolve_user(self, request, target):
        token = self._parse_permission_token_from_request(request)
        if (token is not None) and (token.target == target):
            return token.gestalt
        else:
            return None

    def get_url_with_permission_token(self, target, gestalt, url):
        """ append the secret token to a private resource URL

        A permission token is generated if it did not exist before.
        """
        permission_token = PermissionToken.get_permission_token(
            gestalt, target, self.feature_key, create_if_missing=True)
        # we can safely asssume that usernames and permission tokens need no escaping
        return "{}?token={}:{}".format(url, gestalt.user.username, permission_token.secret_key)


class BasicAuthUserResolver:

    def resolve_user(self, request, target):
        """ retrieve a gestalt that was authenticated via HTTP authentication

        Fail silently and return None if no HTTP authentication data was transmitted. An HTTP
        authentication can be forced later by responding with a 401 HTTP status code. This relaxed
        approach allows to combine this authentication method with other fallback methods.
        """
        auth = BasicAuthentication()
        try:
            result = auth.authenticate(request)
        except (exceptions.NotAuthenticated, exceptions.AuthenticationFailed):
            return None
        if result is None:
            return None
        else:
            return result[0].gestalt


class ChainUserResolver:

    def __init__(self, resolvers):
        self.resolvers = tuple(resolvers)

    def resolve_user(self, request, target):
        for resolver in self.resolvers:
            user = resolver.resolve_user(request, target)
            if user:
                return user
        return None

    def get_url_with_permission_token(self, target, gestalt, url):
        for resolver in self.resolvers:
            if hasattr(resolver, "get_url_with_permission_token"):
                return getattr(resolver, "get_url_with_permission_token")(target, gestalt, url)
        raise NotImplementedError


def get_user_resolver(feature_key):
    return ChainUserResolver([BasicAuthUserResolver(), PermissionTokenUserResolver(feature_key)])
