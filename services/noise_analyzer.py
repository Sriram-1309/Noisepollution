"""
Noise Analyzer - Performs statistical analysis, time-series aggregation,
and automated violation detection using Pandas and NumPy.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from models.noise_reading import NoiseReading
from models.sensor import Sensor
from models.zone import Zone
from models.noise_limit_rule import NoiseLimitRule
from models.violation import Violation


class NoiseAnalyzer:
    """Analyzes noise readings to produce statistics, trends, and detect violations."""

    def __init__(self, db_manager):
        self.db = db_manager

    def get_dashboard_stats(self):
        """Compute all dashboard KPI statistics from actual data.

        Returns:
            dict: Dashboard statistics including sensor counts, averages, violations, risk level
        """
        sensors = Sensor.get_all(self.db)
        total_sensors = len(sensors)
        active_sensors = sum(1 for s in sensors if s.get('status') == 'online')

        avg_noise = NoiseReading.get_average(self.db)
        violation_count = Violation.get_count(self.db)

        # Count sensitive locations (schools + hospitals)
        zones = Zone.get_all(self.db)
        monitored_sensitive = sum(1 for z in zones if z['zone_type'] in ('school', 'hospital'))

        # Highest reading
        max_reading = NoiseReading.get_max(self.db)
        max_noise = {
            'level': max_reading['noise_level_db'] if max_reading else 0,
            'sensor_name': max_reading.get('sensor_name', 'N/A') if max_reading else 'N/A',
            'location': max_reading.get('zone_name', 'N/A') if max_reading else 'N/A',
            'timestamp': max_reading.get('timestamp', '') if max_reading else ''
        }

        # Determine risk level based on average noise and violations
        if avg_noise > 75 or violation_count > 50:
            risk_level = 'Critical'
        elif avg_noise > 65 or violation_count > 25:
            risk_level = 'High'
        elif avg_noise > 55 or violation_count > 10:
            risk_level = 'Moderate'
        else:
            risk_level = 'Low'

        # Recent activity - latest violations
        recent_violations = Violation.get_all(self.db, limit=10)
        recent_activity = []
        for v in recent_violations:
            recent_activity.append({
                'type': 'violation',
                'message': f"Noise violation at {v.get('location_name', 'Unknown')} - {v['noise_level_db']} dB ({v['severity']})",
                'timestamp': v['timestamp'],
                'severity': v['severity']
            })

        return {
            'total_sensors': total_sensors,
            'active_sensors': active_sensors,
            'avg_noise_level': avg_noise,
            'violation_count': violation_count,
            'monitored_sensitive': monitored_sensitive,
            'max_noise': max_noise,
            'risk_level': risk_level,
            'recent_activity': recent_activity
        }

    def get_hourly_trends(self, sensor_id=None, zone_id=None, date=None):
        """Get average noise levels grouped by hour.

        Returns:
            dict: {labels: ['00:00',...,'23:00'], data: [avg_db,...]}
        """
        filters = {}
        if sensor_id:
            filters['sensor_id'] = sensor_id
        if zone_id:
            filters['zone_id'] = zone_id
        if date:
            filters['start_date'] = date + 'T00:00:00'
            filters['end_date'] = date + 'T23:59:59'

        readings = NoiseReading.get_all(self.db, filters=filters, limit=10000)

        if not readings:
            return {'labels': [f'{h:02d}:00' for h in range(24)], 'data': [0] * 24}

        df = pd.DataFrame(readings)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour

        hourly = df.groupby('hour')['noise_level_db'].mean()

        labels = [f'{h:02d}:00' for h in range(24)]
        data = [round(hourly.get(h, 0), 1) for h in range(24)]

        return {'labels': labels, 'data': data}

    def get_daily_averages(self, sensor_id=None, zone_id=None, days=7):
        """Get daily average noise levels.

        Returns:
            dict: {labels: ['2026-10-06',...], data: [avg_db,...]}
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        filters = {'start_date': start_date.isoformat(), 'end_date': end_date.isoformat()}
        if sensor_id:
            filters['sensor_id'] = sensor_id
        if zone_id:
            filters['zone_id'] = zone_id

        readings = NoiseReading.get_all(self.db, filters=filters, limit=10000)

        if not readings:
            labels = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
            return {'labels': labels, 'data': [0] * days}

        df = pd.DataFrame(readings)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date

        daily = df.groupby('date')['noise_level_db'].mean()

        labels = []
        data = []
        for i in range(days):
            d = (start_date + timedelta(days=i)).date()
            labels.append(str(d))
            data.append(round(daily.get(d, 0), 1))

        return {'labels': labels, 'data': data}

    def get_zone_comparison(self):
        """Compare noise levels across all zones.

        Returns:
            list: [{zone_name, zone_type, avg_noise, max_noise, min_noise, reading_count}]
        """
        readings = NoiseReading.get_all(self.db, limit=50000)
        if not readings:
            return []

        df = pd.DataFrame(readings)
        if 'zone_name' not in df.columns or df['zone_name'].isna().all():
            return []

        grouped = df.groupby(['zone_name', 'zone_type']).agg(
            avg_noise=('noise_level_db', 'mean'),
            max_noise=('noise_level_db', 'max'),
            min_noise=('noise_level_db', 'min'),
            reading_count=('noise_level_db', 'count')
        ).reset_index()

        result = []
        for _, row in grouped.iterrows():
            result.append({
                'zone_name': row['zone_name'],
                'zone_type': row['zone_type'],
                'avg_noise': round(row['avg_noise'], 1),
                'max_noise': round(row['max_noise'], 1),
                'min_noise': round(row['min_noise'], 1),
                'reading_count': int(row['reading_count'])
            })

        return sorted(result, key=lambda x: x['avg_noise'], reverse=True)

    def get_peak_hours(self, sensor_id=None, zone_id=None):
        """Identify peak noise hours.

        Returns:
            list: [{hour, avg_noise, reading_count}] sorted by avg_noise desc
        """
        filters = {}
        if sensor_id:
            filters['sensor_id'] = sensor_id
        if zone_id:
            filters['zone_id'] = zone_id

        readings = NoiseReading.get_all(self.db, filters=filters, limit=50000)
        if not readings:
            return []

        df = pd.DataFrame(readings)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour

        hourly = df.groupby('hour').agg(
            avg_noise=('noise_level_db', 'mean'),
            reading_count=('noise_level_db', 'count')
        ).reset_index()

        result = []
        for _, row in hourly.iterrows():
            result.append({
                'hour': int(row['hour']),
                'avg_noise': round(row['avg_noise'], 1),
                'reading_count': int(row['reading_count'])
            })

        return sorted(result, key=lambda x: x['avg_noise'], reverse=True)

    def detect_violations(self):
        """Scan all readings and create violation records for those exceeding limits.

        Only processes readings that don't already have a violation record.

        Returns:
            int: Number of new violations detected
        """
        # Get readings that don't already have violations
        query = '''
            SELECT nr.*, s.name as sensor_name, z.zone_type, z.name as zone_name
            FROM noise_readings nr
            JOIN sensors s ON nr.sensor_id = s.id
            LEFT JOIN zones z ON nr.zone_id = z.id
            WHERE nr.id NOT IN (SELECT COALESCE(reading_id, 0) FROM violations)
        '''
        readings = self.db.execute_query(query)

        if not readings:
            return 0

        new_violations = 0
        for reading in readings:
            zone_type = reading.get('zone_type')
            if not zone_type:
                continue

            # Get the applicable limit
            try:
                ts = datetime.fromisoformat(reading['timestamp'])
                hour = ts.hour
            except (ValueError, TypeError):
                hour = 12  # Default to daytime

            limit = NoiseLimitRule.get_applicable_limit_for_zone(self.db, zone_type, hour)
            noise_level = reading['noise_level_db']

            if noise_level > limit:
                exceedance = round(noise_level - limit, 1)
                severity = Violation.get_severity(exceedance)

                violation_data = {
                    'reading_id': reading['id'],
                    'sensor_id': reading['sensor_id'],
                    'zone_id': reading.get('zone_id'),
                    'timestamp': reading['timestamp'],
                    'noise_level_db': noise_level,
                    'applicable_limit_db': limit,
                    'exceedance_db': exceedance,
                    'zone_type': zone_type,
                    'severity': severity,
                    'location_name': reading.get('zone_name', reading.get('sensor_name', '')),
                    'latitude': reading.get('latitude', 0),
                    'longitude': reading.get('longitude', 0)
                }
                Violation.create(self.db, violation_data)
                new_violations += 1

        return new_violations

    def get_time_series(self, sensor_id=None, zone_id=None,
                        start_date=None, end_date=None, interval='hour'):
        """Get time-series data with configurable interval.

        Returns:
            dict: {labels: [...], datasets: [{label, data}]}
        """
        filters = {}
        if sensor_id:
            filters['sensor_id'] = sensor_id
        if zone_id:
            filters['zone_id'] = zone_id
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date

        readings = NoiseReading.get_all(self.db, filters=filters, limit=50000)
        if not readings:
            return {'labels': [], 'datasets': []}

        df = pd.DataFrame(readings)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp').sort_index()

        # Resample based on interval
        freq = 'h' if interval == 'hour' else 'D'
        resampled = df['noise_level_db'].resample(freq).mean().dropna()

        labels = [t.strftime('%Y-%m-%d %H:%M') if interval == 'hour' else t.strftime('%Y-%m-%d')
                  for t in resampled.index]
        data = [round(v, 1) for v in resampled.values]

        return {
            'labels': labels,
            'datasets': [{'label': 'Average Noise Level (dB)', 'data': data}]
        }

