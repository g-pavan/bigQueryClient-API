import os
from flask import Blueprint, redirect, url_for, session, request
from flask_jwt_extended import JWTManager
import msal
import requests
from config import AzureADConfig
from user_management.user import user_manager

auth_bp = Blueprint('auth', __name__)

# Azure AD app configurations
scope = ["user.read"]

msal_app = msal.ConfidentialClientApplication(
    AzureADConfig.CLIENT_ID,
    authority=AzureADConfig.AUTHORITY,   
    client_credential=AzureADConfig.CLIENT_SECRET
)

# Define a base URL for your application
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')

def get_user_data(access_token):
    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(AzureADConfig.GRAPH_API_ENDPOINT, headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        return user_data
    else:
        return {}

def requires_auth(func):
    def wrapper(*args, **kwargs):
        if user_manager.get_access_token() is None:
            # Store the original URL in the session
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return wrapper

@auth_bp.route('/')
@requires_auth
def home():
    
    print("Current user details: ", user_manager.get_user_profile())

    # Redirect to Swagger home URL
    return redirect(f'{BASE_URL}/apidocs/#/')

@auth_bp.route('/login')
def login():
    # Redirect to Azure AD for login
    auth_url = msal_app.get_authorization_request_url(
        scopes=scope,
        redirect_uri=f'{BASE_URL}/get_token'  # Dynamically set the redirect URI
    )
    return redirect(auth_url)



@auth_bp.route('/get_token')
def get_token():
    if 'code' in request.args:

        # Exchange authorization code for access token
        token_response = msal_app.acquire_token_by_authorization_code(
            request.args['code'],
            scopes=scope,
            redirect_uri=f'{BASE_URL}/get_token'
        )

        if 'access_token' in token_response:
            user_manager.set_access_token(token_response['access_token'])
            user_manager.set_user_profile(get_user_data(user_manager.get_access_token()))

            # Redirect the user back to the original URL or Swagger home URL if not stored
            return redirect(session.get('original_url', f'{BASE_URL}/apidocs/#/'))
        else:
            return 'Failed to retrieve access token'
    else:
        return 'Authorization code not found in the request'

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(session.get('original_url', f'{BASE_URL}'))
