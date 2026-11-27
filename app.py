"""
Noise Pollution Intelligence Dashboard - Main Flask Application
================================================================
Entry point for the web application. Initializes database, registers
blueprints, seeds demo data on first run, and serves all pages.
"""
from flask import Flask, render_template, jsonify, request
from database.db_manager import DatabaseManager
from models.zone import Zone
from services.simulator import SensorDataSimulator
from services.noise_analyzer import NoiseAnalyzer

# Import blueprints
from routes.dashboard import dashboard_bp
from routes.sensors import sensors_bp
from routes.zones import zones_bp
from routes.analytics import analytics_bp
from routes.violations import violations_bp
from routes.reports import reports_bp
from routes.settings import settings_bp, hotspots_bp

import config


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.SECRET_KEY

    # Initialize database
    db_manager = DatabaseManager()
    db_manager.init_db()
    app.config['DB_MANAGER'] = db_manager

    # Seed demo data if database is empty
    zones = Zone.get_all(db_manager)
    if not zones:
        print("[App] No data found. Seeding demo data...")
        simulator = SensorDataSimulator(db_manager)
        simulator.seed_initial_data()
        analyzer = NoiseAnalyzer(db_manager)
        violations_count = analyzer.detect_violations()
        print(f"[App] Detected {violations_count} initial violations.")

    # Register API blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(sensors_bp)
    app.register_blueprint(zones_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(violations_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(hotspots_bp)

    # ---- Page Routes (render HTML templates) ----

    @app.route('/')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/map')
    def noise_map():
        return render_template('map.html')

    @app.route('/sensors')
    def sensors_page():
        return render_template('sensors.html')

    @app.route('/zones')
    def zones_page():
        return render_template('zones.html')

    @app.route('/violations')
    def violations_page():
        return render_template('violations.html')

    @app.route('/analytics')
    def analytics_page():
        return render_template('analytics.html')

    @app.route('/hotspots')
    def hotspots_page():
        return render_template('hotspots.html')

    @app.route('/reports')
    def reports_page():
        return render_template('reports.html')

    @app.route('/settings')
    def settings_page():
        return render_template('settings.html')

    # ---- Simulation Routes ----

    @app.route('/api/simulate/generate', methods=['POST'])
    def simulate_generate():
        """Generate new simulated readings."""
        try:
            data = request.get_json() or {}
            num_readings = data.get('num_readings', 500)
            hours_back = data.get('hours_back', 48)
            simulator = SensorDataSimulator(db_manager)
            count = simulator.generate_readings(num_readings=num_readings, hours_back=hours_back)
            # Auto-detect violations
            analyzer = NoiseAnalyzer(db_manager)
            v_count = analyzer.detect_violations()
            return jsonify({
                'count': count,
                'violations_detected': v_count,
                'message': f'Generated {count} readings, detected {v_count} new violations'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/simulate/reset', methods=['POST'])
    def simulate_reset():
        """Reset readings and violations (keep sensors/zones)."""
        try:
            simulator = SensorDataSimulator(db_manager)
            simulator.reset_data()
            return jsonify({'message': 'All readings and violations cleared'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/simulate/seed', methods=['POST'])
    def simulate_seed():
        """Full reset and re-seed all demo data."""
        try:
            simulator = SensorDataSimulator(db_manager)
            simulator.full_reset()
            analyzer = NoiseAnalyzer(db_manager)
            v_count = analyzer.detect_violations()
            return jsonify({'message': f'Demo data re-seeded. {v_count} violations detected.'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ---- Error Handlers ----

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Endpoint not found'}), 404
        return render_template('dashboard.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Internal server error'}), 500

    return app


# Create the app instance
app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("  Noise Pollution Intelligence Dashboard")
    print("  Monitor noise. Detect hotspots. Build quieter cities.")
    print("=" * 60)
    print("  Open http://localhost:5000 in your browser")
    print("=" * 60)
    app.run(debug=config.DEBUG, port=5000)

