"""Settings API routes - noise limits and hotspot endpoints."""
from flask import Blueprint, jsonify, request, current_app
from models.noise_limit_rule import NoiseLimitRule
from services.hotspot_detector import HotspotDetector

settings_bp = Blueprint('settings_bp', __name__, url_prefix='/api/settings')


@settings_bp.route('/limits')
def get_limits():
    """Get all noise limit rules."""
    try:
        db = current_app.config['DB_MANAGER']
        limits = NoiseLimitRule.get_all(db)
        return jsonify(limits)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/limits', methods=['POST'])
def create_limit():
    """Create a new noise limit rule."""
    try:
        db = current_app.config['DB_MANAGER']
        data = request.get_json()
        if not data or not data.get('zone_type'):
            return jsonify({'error': 'zone_type is required'}), 400
        rule_id = NoiseLimitRule.create(db, data)
        if rule_id:
            return jsonify({'id': rule_id, 'message': 'Rule created successfully'}), 201
        return jsonify({'error': 'Failed to create rule (zone_type may already exist)'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/limits/<int:rule_id>', methods=['PUT'])
def update_limit(rule_id):
    """Update a noise limit rule."""
    try:
        db = current_app.config['DB_MANAGER']
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        success = NoiseLimitRule.update(db, rule_id, data)
        if success:
            return jsonify({'message': 'Rule updated successfully'})
        return jsonify({'error': 'Rule not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/limits/<int:rule_id>', methods=['DELETE'])
def delete_limit(rule_id):
    """Delete a noise limit rule."""
    try:
        db = current_app.config['DB_MANAGER']
        success = NoiseLimitRule.delete(db, rule_id)
        if success:
            return jsonify({'message': 'Rule deleted successfully'})
        return jsonify({'error': 'Rule not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- Hotspot API endpoints ---
hotspots_bp = Blueprint('hotspots_bp', __name__, url_prefix='/api/hotspots')


@hotspots_bp.route('/')
def get_hotspots():
    """Get top noise pollution hotspots."""
    try:
        db = current_app.config['DB_MANAGER']
        detector = HotspotDetector(db)
        top_n = request.args.get('top_n', 5, type=int)
        hotspots = detector.get_hotspots(top_n=top_n)
        return jsonify(hotspots)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@hotspots_bp.route('/stats')
def get_stats():
    """Get zone-level statistics."""
    try:
        db = current_app.config['DB_MANAGER']
        detector = HotspotDetector(db)
        zone_id = request.args.get('zone_id')
        stats = detector.get_zone_statistics(zone_id=zone_id)
        return jsonify({'zone_statistics': stats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@hotspots_bp.route('/recommendations')
def get_recommendations():
    """Get actionable recommendations."""
    try:
        db = current_app.config['DB_MANAGER']
        detector = HotspotDetector(db)
        recs = detector.get_recommendations()
        return jsonify(recs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

