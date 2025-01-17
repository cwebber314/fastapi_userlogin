"""

Start with:

    flask --app app run --debug --port=8000 --host=0.0.0.0
"""
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import os

from flask import Flask, request, redirect, session
from flask.json import jsonify

# Allow http for dev
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# This information is obtained upon registration of a new GitHub
client_id = "124232cb-ac07-49f0-af6f-cc12bfea035e"
client_secret = os.getenv('ENTRA_CLIENT_SECRET')
authorization_base_url = 'https://login.microsoftonline.com/d92c6fc3-4ea6-49b0-928e-66084caad3c6/oauth2/v2.0/authorize'
token_url = 'https://login.microsoftonline.com/d92c6fc3-4ea6-49b0-928e-66084caad3c6/oauth2/v2.0/token'
redirect_uri = 'http://localhost:8000/oauth-callback'
secret_key = "NoMoreSecrets"
scope = ['User.Read']

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key

@app.route("/login")
def login():
    oauth_session = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
    authorization_url, state = oauth_session.authorization_url(authorization_base_url)

    print(authorization_url)
    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route("/oauth-callback")
def callback():
    oauth_session = OAuth2Session(client_id, state=session['oauth_state'], redirect_uri=redirect_uri)
    token = oauth_session.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)
    # print("callback")
    # print(token)
    # Return a protected resource to show that we are authenticated
    # This has the "id" and "userPrincipalName" which are very important to other tools
    return jsonify(oauth_session.get('https://graph.microsoft.com/v1.0/me').json())
