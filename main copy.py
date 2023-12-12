import os
import yaml
import json
from flask import Flask, request, jsonify
from flasgger import Swagger


from bigQueryInterface.bigQueryConnector import BigQueryConnector
from config import project_id, dataset_id, table_id

app = Flask(__name__)


# Load YAML specification from file
with open('api_documentation.yaml', 'r') as file:
    swagger_config = yaml.safe_load(file)

Swagger(app, template=swagger_config)



bq_connector = BigQueryConnector()
bq_connector.connect_to_project(project_id)
bq_connector.connect_to_dataset(dataset_id)
bq_connector.connect_to_table(table_id)


@app.route('/connect_to_project', methods=['GET'])
def connect_to_project():
    
    try:
        project_id = request.args.get('project_id')

        bq_connector.connect_to_project(project_id)

        return jsonify({'success': True, 'message': f'Connected to project {project_id}'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

@app.route('/connect_to_dataset', methods=['GET'])
def connect_to_dataset():
   
    try:
        dataset_id = request.args.get('dataset_id')

        bq_connector.connect_to_dataset(dataset_id)

        return jsonify({'success': True, 'message': f'Connected to dataset {dataset_id}'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

@app.route('/connect_to_table', methods=['GET'])
def connect_to_table():
    
    try:
        table_id = request.args.get('table_id')

        bq_connector.connect_to_table(table_id)

        return jsonify({'success': True, 'message': f'Connected to table {table_id}'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

@app.route('/get_table_data', methods=['GET'])
def get_table_data():
    try:
        limit = request.args.get('limit', default=10, type=int)

        df = bq_connector.get_table_data_as_dataframe(limit)
        data = df.to_dict(orient='records')

        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    
@app.route('/filter_table_data', methods=['GET'])
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
    # http://127.0.0.1:8080/apidocs/
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
