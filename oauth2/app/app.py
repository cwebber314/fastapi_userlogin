"""
We get a JWT token back from microsoft which has the email, name and other info 
for the user. This comes back encrypted using RS256 and the public key from
https://login.microsoftonline.com/d92c6fc3-4ea6-49b0-928e-66084caad3c6/discovery/v2.0/keys

The get_id_email() fails because the callback from microsoft doesn't contain
everything we care about. Add the scope User.Read to the authorization request to 
make everything work
"""
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Request
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback
from httpx_oauth.oauth2 import OAuth2

from starlette.middleware.base import BaseHTTPMiddleware
import traceback
import pdb 

from app.db import User, create_db_and_tables
from app.schemas import UserCreate, UserRead, UserUpdate
from app.users import (
    SECRET,
    auth_backend,
    current_active_user,
    fastapi_users,
    oauth_client,
)

# async def attach_debugger_on_exception(request: Request, call_next):
#     try:
#         response = await call_next(request)
#     except Exception:
#         traceback.print_exc()
#         # `set_trace` would create a breakpoint but the stack would stop here.
#         # `post_mortem` sets the relevant context to be where the exception happened.
#         import pdb
#         pdb.post_mortem()
#         raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
# app.add_middleware(BaseHTTPMiddleware, dispatch=attach_debugger_on_exception)

oauth2_authorize_callback = OAuth2AuthorizeCallback(oauth_client, "oauth-callback")

@app.get("/oauth-callback", name="oauth-callback")
async def oauth_callback(access_token_state=Depends(oauth2_authorize_callback)):
    print("oauth_callback")
    pdb.set_trace()
    token, state = access_token_state
    # Do something useful

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
app.include_router(
    fastapi_users.get_oauth_router(oauth_client, auth_backend, SECRET),
    prefix="/auth/entra",
    tags=["auth"],
)


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}