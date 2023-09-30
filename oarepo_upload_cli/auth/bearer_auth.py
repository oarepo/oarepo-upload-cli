from .token_auth import TokenAuthentication


class BearerAuthentication(TokenAuthentication):
    def __init__(self, token: str):
        super().__init__("Authorization", f"Bearer {token}")
