"""Example OAuth2 use
"""

from fastapi import FastAPI, Depends
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback
from httpx_oauth.oauth2 import OAuth2
import dotenv
import os
import asyncio
import urllib

app = FastAPI()

REDIRECT_URI = 'https://openidconnect.net/callback'

# Called "OIDC Client ID" in openidconnect.net debugger
CLIENT_ID = '124232cb-ac07-49f0-af6f-cc12bfea035e'

# Called "OIDC Client Secret" in  openidconnect.net debugger
CLIENT_SECRET = os.getenv('ENTRA_CLIENT_SECRET')

# Called "Authorization Token Endpoint" in openidconnect.net debugger
AUTHORIZE_ENDPOINT = 'https://login.microsoftonline.com/d92c6fc3-4ea6-49b0-928e-66084caad3c6/oauth2/v2.0/authorize'

# Called "Token Endpoint" in openidconnect.net debugger
ACCESS_TOKEN_ENDPOINT = 'https://login.microsoftonline.com/d92c6fc3-4ea6-49b0-928e-66084caad3c6/oauth2/v2.0/token'

# Note that refresh_token_endpoint and revoke_token_endpoint are optional
# since not every services propose to refresh and revoke tokens.

client = OAuth2(
    CLIENT_ID,
    CLIENT_SECRET,
    AUTHORIZE_ENDPOINT,
    ACCESS_TOKEN_ENDPOINT,
    # refresh_token_endpoint="REFRESH_TOKEN_ENDPOINT",
    # revoke_token_endpoint="REVOKE_TOKEN_ENDPOINT",
)
oauth2_authorize_callback = OAuth2AuthorizeCallback(client, "oauth-callback")

async def main():
    # authorization_url = await client.get_authorization_url(
    #     REDIRECT_URI, scope=["openid"],
    # )
    authorization_url = await client.get_authorization_url(
        REDIRECT_URI, scope=["openid"],
    )


    print("I got the autorization URL")
    print(authorization_url)
    

    # Should look like this
    # https://login.microsoftonline.com/d92c6fc3-4ea6-49b0-928e-66084caad3c6/oauth2/v2.0/authorize?
    # client_id=124232cb-ac07-49f0-af6f-cc12bfea035e
    # &redirect_uri= https://openidconnect.net/callback
    # &scope=openid email profile
    # &response_type=code
    # &state=27f355f49788669a463f04e0a688f941f3bc082e
    # &audience={CLIENT_SECRET}

    # TODO: I need the damn CODE I should get this from the authorization_url.
    # The code goes to the redirect URI 
    # Get the access token, make a request to your token endpoint
    access_token = await client.get_access_token(CODE, REDIRECT_URI)
    print(access_token)
    return 

if __name__ == '__main__':
    asyncio.run(main())

# @app.get("/oauth-callback", name="oauth-callback")
# async def oauth_callback(access_token_state=Depends(oauth2_authorize_callback)):
#     token, state = access_token_state
#     # Do something useful


