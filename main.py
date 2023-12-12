import os
import yaml
from flask import Flask
from flasgger import Swagger
from bigQueryInterface.bigQueryConnector import BigQueryConnector

from config import project_id, dataset_id, table_id

from validation.authetication import auth_bp  # Update the import path
from bigQuery_api.connect_endpoints import connect_endpoints
from bigQuery_api.data_endpoints import data_endpoints

app = Flask(__name__)

# Load YAML specification from file
with open('api_documentation.yaml', 'r') as file:
    swagger_config = yaml.safe_load(file)

Swagger(app, template=swagger_config)

app.bq_connector = BigQueryConnector(
    project_id=project_id,
    dataset_id=dataset_id,
    table_id=table_id
)

# Use the environment variable for the secret key
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback_random_secret_key')

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(connect_endpoints, url_prefix='/connect')
app.register_blueprint(data_endpoints, url_prefix='/data')


if __name__ == '__main__':
    # http://127.0.0.1:5000/apidocs/
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
