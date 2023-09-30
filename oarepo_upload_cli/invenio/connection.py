import requests

from oarepo_upload_cli.exceptions import (
    RepositoryCommunicationException,
    ExceptionMessage,
)


class InvenioConnection:
    def __init__(self, config):
        self._config = config
        self._json_headers = {"Content-Type": "application/json"}

    def get(self, url, *, params=None):
        return self.send_request("get", url=url, params=params)

    def post(self, url, *, json=None):
        return self.send_request("post", url=url, json=json)

    def put(self, url, *, json=None, headers=None, data=None):
        return self.send_request("put", url=url, json=json, headers=headers, data=data)

    def delete(self, url):
        return self.send_request("delete", url=url)

    def send_request(self, http_verb, **kwargs):
        try:
            request_method = getattr(globals()["requests"], http_verb)
            headers = kwargs.pop("headers", self._json_headers)
            res = request_method(
                verify=False, auth=self._config.auth, headers=headers, **kwargs
            )
            res.raise_for_status()
        except requests.ConnectionError as conn_err:
            raise RepositoryCommunicationException(
                ExceptionMessage.ConnectionError, conn_err
            ) from conn_err
        except requests.HTTPError as http_err:
            raise RepositoryCommunicationException(
                ExceptionMessage.HTTPError, http_err, res.text, url=kwargs["url"]
            ) from http_err
        except Exception as err:
            raise RepositoryCommunicationException(str(err), err) from err

        return res
