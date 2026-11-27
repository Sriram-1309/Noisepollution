"""Sensor management API routes - CRUD operations."""
from flask import Blueprint, jsonify, request, current_app
from models.sensor import Sensor
from models.noise_reading import NoiseReading

sensors_bp = Blueprint('sensors_bp', __name__, url_prefix='/api/sensors')


@sensors_bp.route('/')
def get_sensors():
    """List all sensors with their latest reading and zone info."""
    try:
        db = current_app.config['DB_MANAGER']
        sensors = Sensor.get_all(db)
        # Attach latest reading for each sensor
        for sensor in sensors:
            latest = NoiseReading.get_latest_by_sensor(db, sensor['id'])
            sensor['latest_reading'] = latest['noise_level_db'] if latest else None
        return jsonify(sensors)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sensors_bp.route('/', methods=['POST'])
def create_sensor():
    """Create a new sensor."""
    try:
        db = current_app.config['DB_MANAGER']
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({'error': 'Sensor name is required'}), 400
        if 'latitude' not in data or 'longitude' not in data:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        sensor_id = Sensor.create(db, data)
        return jsonify({'id': sensor_id, 'message': 'Sensor created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sensors_bp.route('/<int:sensor_id>')
def get_sensor(sensor_id):
    """Get a sensor by ID with recent readings."""
    try:
        db = current_app.config['DB_MANAGER']
        sensor = Sensor.get_by_id(db, sensor_id)
        if not sensor:
            return jsonify({'error': 'Sensor not found'}), 404
        sensor['readings'] = Sensor.get_readings(db, sensor_id, limit=50)
        return jsonify(sensor)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sensors_bp.route('/<int:sensor_id>', methods=['PUT'])
def update_sensor(sensor_id):
    """Update sensor details."""
    try:
        db = current_app.config['DB_MANAGER']
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        success = Sensor.update(db, sensor_id, data)
        if success:
            return jsonify({'message': 'Sensor updated successfully'})
        return jsonify({'error': 'Sensor not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sensors_bp.route('/<int:sensor_id>', methods=['DELETE'])
def delete_sensor(sensor_id):
    """Delete a sensor and its related data."""
    try:
        db = current_app.config['DB_MANAGER']
        success = Sensor.delete(db, sensor_id)
        if success:
            return jsonify({'message': 'Sensor deleted successfully'})
        return jsonify({'error': 'Sensor not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sensors_bp.route('/<int:sensor_id>/readings')
def get_sensor_readings(sensor_id):
    """Get historical readings for a sensor."""
    try:
        db = current_app.config['DB_MANAGER']
        limit = request.args.get('limit', 50, type=int)
        readings = NoiseReading.get_by_sensor(db, sensor_id, limit=limit)
        return jsonify(readings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

