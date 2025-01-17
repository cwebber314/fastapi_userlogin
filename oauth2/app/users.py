import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, IntegerIDMixin, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback
from httpx_oauth.clients.microsoft import MicrosoftGraphOAuth2
from httpx_oauth.oauth2 import OAuth2
import os
from app.db import User, get_user_db

SECRET = "NoMoreSecrets"
REDIRECT_URI = 'https://openidconnect.net/callback'
# Called "OIDC Client ID" in openidconnect.net debugger
CLIENT_ID = '124232cb-ac07-49f0-af6f-cc12bfea035e'
# Called "OIDC Client Secret" in  openidconnect.net debugger
CLIENT_SECRET = os.getenv('ENTRA_CLIENT_SECRET')
# Called "Authorization Token Endpoint" in openidconnect.net debugger
AUTHORIZE_ENDPOINT = 'https://login.microsoftonline.com/d92c6fc3-4ea6-49b0-928e-66084caad3c6/oauth2/v2.0/authorize'
# Called "Token Endpoint" in openidconnect.net debugger
ACCESS_TOKEN_ENDPOINT = 'https://login.microsoftonline.com/d92c6fc3-4ea6-49b0-928e-66084caad3c6/oauth2/v2.0/token'

SCOPES = ['openid', 'email', 'profile']
TENANT = 'd92c6fc3-4ea6-49b0-928e-66084caad3c6'
# Note that refresh_token_endpoint and revoke_token_endpoint are optional
# since not every services propose to refresh and revoke tokens.

# client = OAuth2(
#     CLIENT_ID,
#     CLIENT_SECRET,
#     AUTHORIZE_ENDPOINT,
#     ACCESS_TOKEN_ENDPOINT,
#     # refresh_token_endpoint="REFRESH_TOKEN_ENDPOINT",
#     # revoke_token_endpoint="REVOKE_TOKEN_ENDPOINT",
# )
# oauth2_authorize_callback = OAuth2AuthorizeCallback(client, "oauth-callback")

client = MicrosoftGraphOAuth2(
    CLIENT_ID,
    CLIENT_SECRET,
    TENANT,
    SCOPES,
    'client name'
)

# class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# Set expiration here 3600 seconds = 60 minutes
def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])
fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)