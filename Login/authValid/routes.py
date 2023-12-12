# authValid/routes.py
from flask import Blueprint, redirect, url_for, request, current_app
import requests
from flask_login import login_user, login_required, logout_user, current_user
from authValid.models import User
from msal import ConfidentialClientApplication

auth_valid = Blueprint('auth_valid', __name__)

msal_app = ConfidentialClientApplication(
    current_app.config_file['CLIENT_ID'],
    authority=current_app.config_file['AUTHORITY'],
    client_credential=current_app.config_file['CLIENT_SECRET']
)

@current_app.login_manager.user_loader
def load_user(user_id):
    return User.load_user(user_id)

def load_or_create_user(account_info, access_token):
    # Try to load the user from the in-memory storage
    user = User.load_user(account_info)

    if user:
        return user

    # If the user doesn't exist, create a new one
    user = User(username=account_info, access_token=access_token)

    # Add the user to the in-memory storage
    User.users[account_info] = user

    return user


scope = ["user.read"]

def get_user_data(access_token):
    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(current_app.config_file['GRAPH_API_ENDPOINT'], headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        return user_data
    else:
        return {}
    
@auth_valid.route('/', methods=['GET'])
def home():
    return 'Welcome to the home page!'

@auth_valid.route('/login')
def login():
    auth_url = msal_app.get_authorization_request_url(scopes=scope, redirect_uri=current_app.config_file['REDIRECT_URI'])
    return redirect(auth_url)

from flask import g

@auth_valid.route('/get_token')
def get_token():
    token_response = msal_app.acquire_token_by_authorization_code(
        request.args['code'],
        scopes=scope,
        redirect_uri=current_app.config_file['REDIRECT_URI']
    )
    if 'error' in token_response:
        return 'Authentication failed'

    # user_info = msal_app.acquire_token_silent(
    #     scope,
    #     account=token_response['account']
    # )
    user_info = get_user_data(token_response['access_token'])

    # Load or create user based on the received token
    user = load_or_create_user(user_info['displayName'], token_response['access_token'])

    # Log in the user
    login_user(user)

    # Store user in Flask application context (g)
    g.user = user

    next_url = request.args.get('next', None)
    return redirect(next_url or url_for('dashboard'))


@auth_valid.route('/dashboard')
@login_required
def dashboard():
    return f'Hello, {current_user.username}! Welcome to the dashboard.'

@auth_valid.route('/logout')
@login_required
def logout():
     # Clear user from the application context
    g.user = None

    # Logout the user
    logout_user()

    # Redirect to the home page
    return redirect(url_for('home'))

