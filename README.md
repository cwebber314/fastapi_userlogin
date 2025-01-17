# FastAPI Users playground

This repo contains several examples of user management and authentication.

- flask_requests_oauthlib: This is a very simple example of authenticating against 
  an OAth2 on azure. It uses [flask] and the [requests_oauthlib](https://requests-oauthlib.readthedocs.io/en/latest/)
- fastapi_users_db: Uses the [FastAPI-Users](https://fastapi-users.github.io/fastapi-users/latest/) library. This stores user info in a database. Users are authenticated against credentials stored in the database.
- fastapi_users_oauth2: Uses the FastAPI-Users library. This authenticates users with azure using OAuth2 

## Azure Setup

Setup an application in azure and add the web redirect uris. Generate a secret and 
store it somewhere safe. 

Screenshot of application in azure:
![azure_app](azure_app.png)

## Python Setup

The setup steps are the same for all of the examples.

setup virtualenv:
```
python -m venv .venv
.venv\scripts\activate
pip install -r requirements.txt
```

You also need the client secret from azure.
```
SET ENTRA_CLIENT_SECRET={client_secret}
```

## flask_requests_oauthlib

To run:
```
cd flask_requests_oauthlib
flask --app app run --debug --port=8000 --host=0.0.0.0
```

To test:
- Visiting [http://localhost:8000/login](http://localhost:8000/login)
- You get redirected to microsoft login page.
- login to the microsoft page
- You are then redirect to `localhost:8000/oauth-callback`
- The flask app on localhost gets your user information from microsoft and displays
  it as json in the browser

## fastapi_users_db

This example:
- Frontend sends a bearer token in the request header
- The token is a self-contained JWT (JSON Web Token) 

The username/credentials are checked and stored against a local sqlite database 

run:
```
cd fastapi_users_db
python main.py
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### Example use

Register a new user:
```
curl --location 'http://127.0.0.1:8000/auth/register' \
--header 'Content-Type: application/json' \
--data-raw '{
    "email": "king.arthur2@camelot.bt",
    "password": "guinevere",
    "full_name": "The King",
    "user_id": "u123456"
}'
```

Login:
```
curl --location 'http://127.0.0.1:8000/auth/jwt/login' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'username=king.arthur@camelot.bt' \
--data-urlencode 'password=guinevere'
```

From the login response save the token:
```
{
    "access_token": "••••••",
    "token_type": "bearer"
}
```

Now you can access the protected route by including the token in the header:
```
curl --location 'http://127.0.0.1:8000/authenticated-route' \
--header 'Authorization: ••••••'
```

### Frontend integration

After login, the frontend saves the JWT in session storage, then adds the token to outgoing API request.

### Creating a superuser

To create a superuser you have to edit the db directly:
```sql
UPDATE user SET is_superuser=1 WHERE id=3
```

## fastapi_users_oauth2

This example:
- Frontend sends a bearer token in the request header
- The token is a self-contained JWT (JSON Web Token) 

The username/credentials are checked using OAuth2 using the HTTPX OAuth library instead of a database. 

### Postman example

GET the authorize route: `http://localhost:8000/auth/entra/authorize?scopes=User.Read`

This returns a reponse like:
```
{
    "authorization_url": "https://login.microsoftonline.com/d92c6fc3-4ea6-49b0-928e-66084caad3c6/oauth2/v2.0/authorize?response_type=code&client_id=124232cb-ac07-49f0-af6f-cc12bfea035e&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fauth%2Fentra%2Fcallback&state=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJmYXN0YXBpLXVzZXJzOm9hdXRoLXN0YXRlIiwiZXhwIjoxNzM3MDk5MjA4fQ.xeLOlEuHw1LAm3yVJcXthCCYQi3C6o2rlrnxZeiHwyc&scope=User.Read&response_mode=query"
}
```

If we open the authorization url in a browser windows we can complete the 
sign in on the microsoft platform. After we login to microsoft, the microsoft 
server calls POSTS to our callback URL `/auth/entra/callback` and returns an access token and id token.

We can decode the id token to get a payload with user information like name and email.

The FastAPI-Users machinary also adds an entry in the db table `user` and `oauth_account`

## Debug: Authentication with Entra

Use the [https://openidconnect.net/#](https://openidconnect.net/#) to debug.
- Use the Discovery Document URL: `https://login.microsoftonline.com/{TENANT_ID}/v2.0/.well-known/openid-configuration` to fill in
    - Authorization Token Endpoint
    - Token Endpoint
    - Token Keys Endpoint
- Tenant ID: Get this from azure, sometimes called the "Tenant ID" or "Directory (tenant) ID"
- OIDC Client ID:  Get this from azure "Application (client) ID"
- scope: `openid email profile User.Read`
- client secret: this is the *Value* for the secret in Entra - it's only available when you first create the secret.
  Note that it's not the secret ID (guid)

Sample params for test azure:
- Tenant ID: `d92c6fc3-4ea6-49b0-928e-66084caad3c6`

This generates the request:
```
https://login.microsoftonline.com/d92c6fc3-4ea6-49b0-928e-66084caad3c6/oauth2/v2.0/authorize? 
client_id=124232cb-ac07-49f0-af6f-cc12bfea035e
&redirect_uri= https://openidconnect.net/callback
&scope=openid
&response_type=code
&state=27f355f49788669a463f04e0a688f941f3bc082e
```
