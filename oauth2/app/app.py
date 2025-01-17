from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

import os
from app.db import User, create_db_and_tables
from app.schemas import UserCreate, UserRead, UserUpdate
from app.users import auth_backend, current_active_user, fastapi_users
from fastapi import FastAPI, Depends
from httpx_oauth.oauth2 import OAuth2
from httpx_oauth.clients.microsoft import MicrosoftGraphOAuth2
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback


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

# Microsoft client
client = MicrosoftGraphOAuth2(
    CLIENT_ID,
    CLIENT_SECRET,
    TENANT,
    SCOPES,
    'client name'
)

# Generic client
# client = OAuth2(CLIENT_ID, 
#                 CLIENT_SECRET, 
#                 AUTHORIZE_ENDPOINT, 
#                 ACCESS_TOKEN_ENDPOINT)

oauth2_authorize_callback = OAuth2AuthorizeCallback(client, "oauth-callback")
app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}

@app.get("/oauth-callback", name="oauth-callback")
async def oauth_callback(access_token_state=Depends(oauth2_authorize_callback)):
    token, state = access_token_state
    print("oauth_callback")
    print(token)
    print(state)
    # Do something useful