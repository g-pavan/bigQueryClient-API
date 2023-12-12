from flask import Blueprint, request, jsonify, current_app
from user_management.user import user_manager
import json

data_endpoints = Blueprint('data_endpoints', __name__)

@data_endpoints.route('/get_table_data', methods=['GET'])
@user_manager.validate_access_token
def get_table_data():
    try:
        limit = request.args.get('limit', default=10, type=int)
        df = current_app.bq_connector.get_table_data_as_dataframe(limit)
        data = df.to_dict(orient='records')
        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    
@data_endpoints.route('/filter_table_data', methods=['GET'])
@user_manager.validate_access_token
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


        df = current_app.bq_connector.get_table_data_as_dataframe()

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

@data_endpoints.route('/filter_row_data', methods=['GET'])
@user_manager.validate_access_token
def filter_row_data():
    try:
        # Get the 'search_value' query parameter
        search_value = request.args.get('search_value', None)

        if search_value is None:
            raise ValueError("Missing 'search_value' parameter")

        df = current_app.bq_connector.get_table_data_as_dataframe()

        # Perform search on all columns for the specified value
        matching_rows = df[df.apply(lambda row: any(str(search_value) in str(cell) for cell in row), axis=1)]

        # Convert the matching rows to a list of records
        data = matching_rows.to_dict(orient='records')

        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404