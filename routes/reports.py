"""Reports API routes - summaries, CSV exports."""
import csv
import io
from flask import Blueprint, jsonify, request, current_app, Response
from models.noise_reading import NoiseReading
from models.violation import Violation
from services.hotspot_detector import HotspotDetector

reports_bp = Blueprint('reports_bp', __name__, url_prefix='/api/reports')


@reports_bp.route('/summary')
def get_summary():
    """Get comprehensive report summary."""
    try:
        db = current_app.config['DB_MANAGER']
        detector = HotspotDetector(db)
        summary = detector.get_report_summary(
            start_date=request.args.get('start_date'),
            end_date=request.args.get('end_date'),
            zone_type=request.args.get('zone_type')
        )
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/export/readings')
def export_readings():
    """Export noise readings as CSV file download."""
    try:
        db = current_app.config['DB_MANAGER']
        filters = {}
        for key in ['sensor_id', 'zone_type', 'start_date', 'end_date']:
            val = request.args.get(key)
            if val:
                filters[key] = val

        readings = NoiseReading.get_all(db, filters=filters if filters else None, limit=50000)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Sensor ID', 'Sensor Name', 'Timestamp', 'Noise Level (dB)',
                          'Latitude', 'Longitude', 'Zone Type', 'Zone Name'])
        for r in readings:
            writer.writerow([r.get('id'), r.get('sensor_id'), r.get('sensor_name', ''),
                             r.get('timestamp'), r.get('noise_level_db'),
                             r.get('latitude'), r.get('longitude'),
                             r.get('zone_type', ''), r.get('zone_name', '')])

        csv_data = output.getvalue()
        return Response(csv_data, mimetype='text/csv',
                        headers={'Content-Disposition': 'attachment; filename=noise_readings.csv'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/export/violations')
def export_violations():
    """Export violations as CSV file download."""
    try:
        db = current_app.config['DB_MANAGER']
        filters = {}
        for key in ['zone_type', 'severity', 'start_date', 'end_date']:
            val = request.args.get(key)
            if val:
                filters[key] = val

        violations = Violation.get_all(db, filters=filters if filters else None, limit=50000)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Sensor ID', 'Sensor Name', 'Location', 'Zone Type',
                          'Timestamp', 'Noise Level (dB)', 'Limit (dB)', 'Exceedance (dB)',
                          'Severity', 'Latitude', 'Longitude'])
        for v in violations:
            writer.writerow([v.get('id'), v.get('sensor_id'), v.get('sensor_name', ''),
                             v.get('location_name', ''), v.get('zone_type', ''),
                             v.get('timestamp'), v.get('noise_level_db'),
                             v.get('applicable_limit_db'), v.get('exceedance_db'),
                             v.get('severity', ''), v.get('latitude'), v.get('longitude')])

        csv_data = output.getvalue()
        return Response(csv_data, mimetype='text/csv',
                        headers={'Content-Disposition': 'attachment; filename=noise_violations.csv'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

