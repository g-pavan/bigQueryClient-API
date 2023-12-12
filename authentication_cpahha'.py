from flask import Flask, redirect, url_for, session, request, render_template
import msal
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zDb8Q~IrASuHPJMuBRFikEWtpq2I5Axp2bILcdc9'
app.config['SESSION_TYPE'] = 'filesystem'

# Azure AD app configurations
CLIENT_ID = "5168674a-ec68-44c7-9e89-2b518a59e10a"
CLIENT_SECRET = "zDb8Q~IrASuHPJMuBRFikEWtpq2I5Axp2bILcdc9"
tenant_id = "6de5354b-f23a-492c-b7cb-d04a716bcbc1"
REDIRECT_URI = "http://localhost:5000/get_token"  # Update with your redirect URI
AUTHORITY = "https://login.microsoftonline.com/6de5354b-f23a-492c-b7cb-d04a716bcbc1"  # Update with your Azure AD tenant ID
GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0/me'

scope = ["user.read"]

# MSAL Confidential Client Application
# app_config = {
#     'client_id': CLIENT_ID,
#     'client_secret': CLIENT_SECRET,
#     'authority': AUTHORITY,
# }
# msal_app = msal.ConfidentialClientApplication(**app_config)

msal_app = msal.ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET
)

def get_user_profile(access_token):
    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(GRAPH_API_ENDPOINT, headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        return user_data.get('displayName', 'User')
    else:
        return 'User'

@app.route('/')
def home():
    username = 'User'
    if 'access_token' in session:
        access_token = session['access_token']
        username = get_user_profile(access_token)
    return render_template('home.html', logged_in='access_token' in session, username=username)

@app.route('/login')
def login():
    # Redirect to Azure AD for login
    auth_url = msal_app.get_authorization_request_url(
        scopes = scope,
        redirect_uri = REDIRECT_URI,
    )
    return redirect(auth_url)

@app.route('/get_token')
def get_token():
    if 'code' in request.args:
        # Exchange authorization code for access token
        token_response = msal_app.acquire_token_by_authorization_code(
            request.args['code'],
            scopes = scope,
            redirect_uri = REDIRECT_URI,
        )
        
        if 'access_token' in token_response:
            # Store the token in session (you may want to store it securely)
            session['access_token'] = token_response['access_token']
            return redirect(url_for('home'))
        else:
            return 'Failed to retrieve access token'
    else:
        return 'Authorization code not found in the request'

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)