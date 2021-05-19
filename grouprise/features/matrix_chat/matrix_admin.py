import json
import urllib.request

from grouprise.features.matrix_chat.settings import MATRIX_SETTINGS


class MatrixAdmin:
    """execute administrative requests (not provided by the "nio" package)

    The "nio" package covers all aspects of client-server requests.
    But some tasks may require access to the admin API of an matrix-synapse server (usually below
    /_synapse/admin/).
    """

    def __init__(self, auth_token, api_url=MATRIX_SETTINGS.ADMIN_API_URL):
        self.api_url = api_url
        self.auth_token = auth_token

    def _submit_http_request(self, path, method, data=None):
        if method in {"PUT", "POST"}:
            if data is not None:
                payload = json.dumps(data).encode()
            else:
                payload = b"{}"
        else:
            payload = None
        url = "{}/{}".format(self.api_url.rstrip("/"), path.lstrip("/"))
        request = urllib.request.Request(
            url,
            method=method,
            headers={"Authorization": "Bearer {}".format(self.auth_token)},
            data=payload,
        )
        with urllib.request.urlopen(request) as req:
            response = req.read()
        return json.loads(response)

    def request_get(self, path):
        return self._submit_http_request(path, method="GET")

    def request_put(self, path, data=None):
        return self._submit_http_request(path, method="PUT", data=data)

    def request_post(self, path, data=None):
        return self._submit_http_request(path, method="POST", data=data)
