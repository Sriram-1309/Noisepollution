"""Zone management API routes."""
from flask import Blueprint, jsonify, request, current_app
from models.zone import Zone

zones_bp = Blueprint('zones_bp', __name__, url_prefix='/api/zones')


@zones_bp.route('/')
def get_zones():
    """List all zones with sensor counts."""
    try:
        db = current_app.config['DB_MANAGER']
        zones = Zone.get_all(db)
        return jsonify(zones)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@zones_bp.route('/', methods=['POST'])
def create_zone():
    """Create a new zone."""
    try:
        db = current_app.config['DB_MANAGER']
        data = request.get_json()
        if not data or not data.get('name') or not data.get('zone_type'):
            return jsonify({'error': 'Name and zone_type are required'}), 400
        zone_id = Zone.create(db, data)
        return jsonify({'id': zone_id, 'message': 'Zone created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@zones_bp.route('/<int:zone_id>')
def get_zone(zone_id):
    """Get a zone by ID."""
    try:
        db = current_app.config['DB_MANAGER']
        zone = Zone.get_by_id(db, zone_id)
        if not zone:
            return jsonify({'error': 'Zone not found'}), 404
        return jsonify(zone)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@zones_bp.route('/<int:zone_id>', methods=['PUT'])
def update_zone(zone_id):
    """Update zone details."""
    try:
        db = current_app.config['DB_MANAGER']
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        success = Zone.update(db, zone_id, data)
        if success:
            return jsonify({'message': 'Zone updated successfully'})
        return jsonify({'error': 'Zone not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@zones_bp.route('/<int:zone_id>', methods=['DELETE'])
def delete_zone(zone_id):
    """Delete a zone."""
    try:
        db = current_app.config['DB_MANAGER']
        success = Zone.delete(db, zone_id)
        if success:
            return jsonify({'message': 'Zone deleted successfully'})
        return jsonify({'error': 'Zone not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

