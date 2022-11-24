from requests.auth import AuthBase

class TokenAuth(AuthBase):
    """
    Implements a custom token-based authentication.
    """

    def __init__(self, header_field, token):
        self.header_field = header_field
        self.token = token

    def __call__(self, req):
        req.headers[self.header_field] = f'{self.token}'
        return req