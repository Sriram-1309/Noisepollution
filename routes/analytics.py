"""Analytics API routes - time-series analysis endpoints."""
from flask import Blueprint, jsonify, request, current_app
from services.noise_analyzer import NoiseAnalyzer

analytics_bp = Blueprint('analytics_bp', __name__, url_prefix='/api/analytics')


@analytics_bp.route('/timeseries')
def get_timeseries():
    """Get time-series noise data with configurable filters and interval."""
    try:
        db = current_app.config['DB_MANAGER']
        analyzer = NoiseAnalyzer(db)
        result = analyzer.get_time_series(
            sensor_id=request.args.get('sensor_id'),
            zone_id=request.args.get('zone_id'),
            start_date=request.args.get('start_date'),
            end_date=request.args.get('end_date'),
            interval=request.args.get('interval', 'hour')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/hourly')
def get_hourly():
    """Get hourly noise trends."""
    try:
        db = current_app.config['DB_MANAGER']
        analyzer = NoiseAnalyzer(db)
        result = analyzer.get_hourly_trends(
            sensor_id=request.args.get('sensor_id'),
            zone_id=request.args.get('zone_id'),
            date=request.args.get('date')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/daily')
def get_daily():
    """Get daily average noise levels."""
    try:
        db = current_app.config['DB_MANAGER']
        analyzer = NoiseAnalyzer(db)
        days = request.args.get('days', 7, type=int)
        result = analyzer.get_daily_averages(
            sensor_id=request.args.get('sensor_id'),
            zone_id=request.args.get('zone_id'),
            days=days
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/zones')
def get_zones_comparison():
    """Compare noise levels across zones."""
    try:
        db = current_app.config['DB_MANAGER']
        analyzer = NoiseAnalyzer(db)
        result = analyzer.get_zone_comparison()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/peak-hours')
def get_peak_hours():
    """Get peak noise hours analysis."""
    try:
        db = current_app.config['DB_MANAGER']
        analyzer = NoiseAnalyzer(db)
        result = analyzer.get_peak_hours(
            sensor_id=request.args.get('sensor_id'),
            zone_id=request.args.get('zone_id')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

