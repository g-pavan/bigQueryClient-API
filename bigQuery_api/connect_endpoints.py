from flask import Blueprint, request, jsonify, current_app
from user_management.user import user_manager

connect_endpoints = Blueprint('connect_endpoints', __name__)

@connect_endpoints.route('/project', methods=['GET'])
@user_manager.validate_access_token
def connect_to_project():
    try:
        project_id = request.args.get('project_id')
        current_app.bq_connector.connect_to_project(project_id)
        return jsonify({'success': True, 'message': f'Connected to project {project_id}'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

@connect_endpoints.route('/dataset', methods=['GET'])
@user_manager.validate_access_token
def connect_to_dataset():
    try:
        dataset_id = request.args.get('dataset_id')
        current_app.bq_connector.connect_to_dataset(dataset_id)
        return jsonify({'success': True, 'message': f'Connected to dataset {dataset_id}'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

@connect_endpoints.route('/table', methods=['GET'])
@user_manager.validate_access_token
def connect_to_table():
    try:
        table_id = request.args.get('table_id')
        current_app.bq_connector.connect_to_table(table_id)
        return jsonify({'success': True, 'message': f'Connected to table {table_id}'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404
