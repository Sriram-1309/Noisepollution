"""Violation monitoring API routes."""
from flask import Blueprint, jsonify, request, current_app
from models.violation import Violation
from services.noise_analyzer import NoiseAnalyzer

violations_bp = Blueprint('violations_bp', __name__, url_prefix='/api/violations')


@violations_bp.route('/')
def get_violations():
    """List violations with optional filters."""
    try:
        db = current_app.config['DB_MANAGER']
        filters = {}
        for key in ['zone_type', 'severity', 'start_date', 'end_date', 'sensor_id']:
            val = request.args.get(key)
            if val:
                filters[key] = val
        violations = Violation.get_all(db, filters=filters if filters else None)
        return jsonify(violations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@violations_bp.route('/<int:violation_id>')
def get_violation(violation_id):
    """Get detailed info for a specific violation."""
    try:
        db = current_app.config['DB_MANAGER']
        violation = Violation.get_by_id(db, violation_id)
        if not violation:
            return jsonify({'error': 'Violation not found'}), 404
        return jsonify(violation)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@violations_bp.route('/detect', methods=['POST'])
def detect_violations():
    """Run the violation detection engine on unprocessed readings."""
    try:
        db = current_app.config['DB_MANAGER']
        analyzer = NoiseAnalyzer(db)
        count = analyzer.detect_violations()
        return jsonify({'count': count, 'message': f'{count} new violations detected'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@violations_bp.route('/count')
def get_violation_count():
    """Get violation count with optional filters."""
    try:
        db = current_app.config['DB_MANAGER']
        filters = {}
        for key in ['zone_type', 'severity', 'start_date', 'end_date']:
            val = request.args.get(key)
            if val:
                filters[key] = val
        count = Violation.get_count(db, filters=filters if filters else None)
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

