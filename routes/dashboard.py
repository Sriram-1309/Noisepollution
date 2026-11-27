"""Dashboard API routes."""
from flask import Blueprint, jsonify, current_app
from services.noise_analyzer import NoiseAnalyzer

dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='/api/dashboard')


@dashboard_bp.route('/stats')
def get_stats():
    """Get all dashboard statistics computed from actual data."""
    try:
        db = current_app.config['DB_MANAGER']
        analyzer = NoiseAnalyzer(db)
        stats = analyzer.get_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

