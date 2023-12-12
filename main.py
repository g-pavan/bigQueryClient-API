import os
import yaml
import json
from flask import Flask, request, jsonify, redirect, url_for
from flasgger import Swagger
import requests
from msal import ConfidentialClientApplication
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from bigQueryInterface.bigQueryConnector import BigQueryConnector
from config import project_id, dataset_id, table_id

app = Flask(__name__)


# Define a decorator to add CORS headers to your routes
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return response

# Apply the decorator to all routes
app.after_request(add_cors_headers)

app.config.from_pyfile('config.py', silent=True)  # Add this line to load the configuration silently
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Load YAML specification from file
with open('api_documentation.yaml', 'r') as file:
    swagger_config = yaml.safe_load(file)

Swagger(app, template=swagger_config)

class User(UserMixin):
    users = {}  # In-memory storage for users

    def __init__(self, username, access_token):
        self.username = username
        self.access_token = access_token
    
    def get_id(self):
        return self.username

    @classmethod
    def load_user(cls, username):
        return cls.users.get(username)



bq_connector = BigQueryConnector()
bq_connector.connect_to_project(project_id)
bq_connector.connect_to_dataset(dataset_id)
bq_connector.connect_to_table(table_id)

msal_app = ConfidentialClientApplication(
    app.config['CLIENT_ID'],
    authority=app.config['AUTHORITY'],
    client_credential=app.config['CLIENT_SECRET']
)

@login_manager.user_loader
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
    headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.get(app.config['GRAPH_API_ENDPOINT'], headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        return user_data
    else:
        return {}
    
@app.route('/')
@login_required
def home():
    return redirect('/apidocs/')

@app.route('/login')
def login():
    auth_url = msal_app.get_authorization_request_url(scopes=scope, redirect_uri=app.config['REDIRECT_URI'])
    return redirect(auth_url)


@app.route('/get_token')
def get_token():
    token_response = msal_app.acquire_token_by_authorization_code(
        request.args['code'],
        scopes=scope,
        redirect_uri=app.config['REDIRECT_URI']
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

    # # Store user in Flask application context (g)
    # g.user = user

    next_url = request.args.get('next', None)
    return redirect(next_url or url_for('dashboard'))


@app.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
     # Clear user from the application context
    # g.user = None

    # Logout the user
    logout_user()

    # Redirect to the home page
    return redirect(url_for('home'))


@app.route('/connect_to_project', methods=['GET'])
@login_required
def connect_to_project():
    
    try:
        project_id = request.args.get('project_id')

        bq_connector.connect_to_project(project_id)

        return jsonify({'success': True, 'message': f'Connected to project {project_id}'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

@app.route('/connect_to_dataset', methods=['GET'])
@login_required
def connect_to_dataset():
   
    try:
        dataset_id = request.args.get('dataset_id')

        bq_connector.connect_to_dataset(dataset_id)

        return jsonify({'success': True, 'message': f'Connected to dataset {dataset_id}'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

@app.route('/connect_to_table', methods=['GET'])
@login_required
def connect_to_table():
    
    try:
        table_id = request.args.get('table_id')

        bq_connector.connect_to_table(table_id)

        return jsonify({'success': True, 'message': f'Connected to table {table_id}'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

@app.route('/get_table_data', methods=['GET'])
@login_required
def get_table_data():
    try:
        limit = request.args.get('limit', default=10, type=int)

        df = bq_connector.get_table_data_as_dataframe(limit)
        data = df.to_dict(orient='records')

        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    
@app.route('/filter_table_data', methods=['GET'])
@login_required
def filter_table_data():
    try:
        # Get the 'filters' query parameter as a JSON string
        filters_json = request.args.get('filters', None)
        
        if filters_json is not None:
            # Parse the JSON object if 'filters' is provided
            filters = json.loads(filters_json)
        else:
            # If 'filters' is not provided, assume individual query parameters
            filters = {param: request.args.get(param) for param in request.args if param != 'limit'}


        df = bq_connector.get_table_data_as_dataframe()

        # Validate filters against DataFrame columns
        invalid_filters = [key for key in filters if key not in df.columns]
        if invalid_filters:
            raise ValueError(f"Invalid filter(s): {', '.join(invalid_filters)}")

        # Validate and apply dynamic filters to the DataFrame
        for key, value in filters.items():
            if key not in df.columns:
                raise ValueError(f"Invalid filter: {key}")
            df = df[df[key] == value]

        # Convert the filtered DataFrame to a list of records
        data = df.to_dict(orient='records')

        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404



if __name__ == '__main__':
    # http://127.0.0.1:5000/apidocs/
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
