"""
Hotspot Detector - Identifies and ranks noise pollution hotspots
using statistical analysis and scoring algorithms.
"""
import numpy as np
from models.zone import Zone
from models.noise_reading import NoiseReading
from models.violation import Violation
from models.noise_limit_rule import NoiseLimitRule


class HotspotDetector:
    """Detects, ranks, and analyzes noise pollution hotspots across zones."""

    def __init__(self, db_manager):
        self.db = db_manager

    def get_hotspots(self, top_n=5):
        """Identify and rank the top noise pollution hotspots.

        Uses a composite scoring formula considering average noise,
        violation count, max noise, and standard deviation.
        Score = avg_noise*0.3 + violation_count*0.4 + max_noise*0.1 + std_dev*0.2

        Returns:
            list: Top hotspots ranked by score
        """
        zones = Zone.get_all(self.db)
        if not zones:
            return []

        hotspots = []
        for zone in zones:
            # Get readings for this zone
            readings = NoiseReading.get_all(self.db, filters={'zone_id': zone['id']}, limit=50000)
            if not readings:
                continue

            noise_values = [r['noise_level_db'] for r in readings]
            avg_noise = float(np.mean(noise_values))
            max_noise = float(np.max(noise_values))
            std_dev = float(np.std(noise_values))

            # Count violations for this zone
            violation_count = Violation.get_count(self.db, filters={'zone_type': zone['zone_type']})

            # Normalize and compute score
            # Higher score = worse hotspot
            score = (avg_noise * 0.3) + (violation_count * 0.4) + (max_noise * 0.1) + (std_dev * 0.2)

            hotspots.append({
                'zone_id': zone['id'],
                'zone_name': zone['name'],
                'zone_type': zone['zone_type'],
                'avg_noise': round(avg_noise, 1),
                'max_noise': round(max_noise, 1),
                'min_noise': round(float(np.min(noise_values)), 1),
                'std_dev': round(std_dev, 1),
                'violation_count': violation_count,
                'reading_count': len(noise_values),
                'score': round(score, 2),
                'latitude': zone['latitude'],
                'longitude': zone['longitude']
            })

        # Sort by score descending and add ranks
        hotspots.sort(key=lambda x: x['score'], reverse=True)
        for i, h in enumerate(hotspots[:top_n]):
            h['rank'] = i + 1

        return hotspots[:top_n]

    def get_zone_statistics(self, zone_id=None):
        """Compute detailed statistics per zone using NumPy.

        Returns:
            list: [{zone_name, mean, median, min, max, std_dev, p25, p75, reading_count, violation_count}]
        """
        zones = Zone.get_all(self.db)
        if not zones:
            return []

        if zone_id:
            zones = [z for z in zones if z['id'] == int(zone_id)]

        stats = []
        for zone in zones:
            readings = NoiseReading.get_all(self.db, filters={'zone_id': zone['id']}, limit=50000)
            if not readings:
                continue

            values = np.array([r['noise_level_db'] for r in readings])
            violation_count = Violation.get_count(self.db, filters={'zone_type': zone['zone_type']})

            stats.append({
                'zone_id': zone['id'],
                'zone_name': zone['name'],
                'zone_type': zone['zone_type'],
                'mean': round(float(np.mean(values)), 1),
                'median': round(float(np.median(values)), 1),
                'min': round(float(np.min(values)), 1),
                'max': round(float(np.max(values)), 1),
                'std_dev': round(float(np.std(values)), 1),
                'percentile_25': round(float(np.percentile(values, 25)), 1),
                'percentile_75': round(float(np.percentile(values, 75)), 1),
                'reading_count': len(values),
                'violation_count': violation_count
            })

        return sorted(stats, key=lambda x: x['mean'], reverse=True)

    def get_sensor_statistics(self, sensor_id=None):
        """Compute statistics for a specific sensor.

        Returns:
            dict: Statistical summary for the sensor
        """
        if not sensor_id:
            return {}

        readings = NoiseReading.get_all(self.db, filters={'sensor_id': sensor_id}, limit=50000)
        if not readings:
            return {}

        values = np.array([r['noise_level_db'] for r in readings])
        return {
            'sensor_id': sensor_id,
            'mean': round(float(np.mean(values)), 1),
            'median': round(float(np.median(values)), 1),
            'min': round(float(np.min(values)), 1),
            'max': round(float(np.max(values)), 1),
            'std_dev': round(float(np.std(values)), 1),
            'reading_count': len(values)
        }

    def get_recommendations(self, hotspots=None):
        """Generate actionable recommendations based on hotspot analysis.

        Returns:
            list: [{priority, zone_name, zone_type, recommendation, details}]
        """
        if hotspots is None:
            hotspots = self.get_hotspots(top_n=10)

        recommendations = []
        for h in hotspots:
            zone_type = h['zone_type']
            avg = h['avg_noise']
            violations = h['violation_count']

            # Get applicable limit
            rule = NoiseLimitRule.get_by_zone_type(self.db, zone_type)
            day_limit = rule['day_limit_db'] if rule else 75

            if zone_type in ('hospital', 'school'):
                if violations > 5:
                    recommendations.append({
                        'priority': 'high',
                        'zone_name': h['zone_name'],
                        'zone_type': zone_type,
                        'recommendation': f"Urgent: Install noise barriers near {h['zone_name']}",
                        'details': f"Average noise {avg} dB exceeds {zone_type} zone limit of {day_limit} dB. "
                                   f"{violations} violations detected. Consider traffic rerouting and sound insulation."
                    })
                elif avg > day_limit * 0.9:
                    recommendations.append({
                        'priority': 'medium',
                        'zone_name': h['zone_name'],
                        'zone_type': zone_type,
                        'recommendation': f"Monitor closely: {h['zone_name']} approaching limit",
                        'details': f"Average noise {avg} dB is close to the {day_limit} dB limit. "
                                   f"Increase monitoring frequency."
                    })
            elif zone_type == 'traffic':
                if avg > day_limit:
                    recommendations.append({
                        'priority': 'high',
                        'zone_name': h['zone_name'],
                        'zone_type': zone_type,
                        'recommendation': f"Implement traffic calming at {h['zone_name']}",
                        'details': f"Average noise {avg} dB exceeds traffic zone limit. "
                                   f"Consider speed limits, no-honking zones, or signal optimization."
                    })
            elif zone_type == 'residential':
                if violations > 3:
                    recommendations.append({
                        'priority': 'medium',
                        'zone_name': h['zone_name'],
                        'zone_type': zone_type,
                        'recommendation': f"Enforce noise regulations at {h['zone_name']}",
                        'details': f"{violations} violations recorded. "
                                   f"Consider noise barriers, green buffer zones, or time-based restrictions."
                    })
            elif violations > 0:
                priority = 'high' if violations > 10 else 'medium' if violations > 3 else 'low'
                recommendations.append({
                    'priority': priority,
                    'zone_name': h['zone_name'],
                    'zone_type': zone_type,
                    'recommendation': f"Review noise sources at {h['zone_name']}",
                    'details': f"Average noise {avg} dB with {violations} violations. "
                               f"Investigate and implement appropriate mitigation measures."
                })

        return sorted(recommendations, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x['priority'], 3))

    def get_report_summary(self, start_date=None, end_date=None, zone_type=None):
        """Generate a comprehensive report summary.

        Returns:
            dict: Complete report with statistics, hotspots, and recommendations
        """
        filters = {}
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        if zone_type:
            filters['zone_type'] = zone_type

        total_readings = NoiseReading.get_count(self.db)
        total_violations = Violation.get_count(self.db, filters=filters if filters else None)

        # Most affected zones
        zone_stats = self.get_zone_statistics()
        most_affected = zone_stats[:5] if zone_stats else []

        # Peak periods
        readings = NoiseReading.get_all(self.db, filters=filters, limit=50000)
        peak_periods = []
        if readings:
            import pandas as pd
            df = pd.DataFrame(readings)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            hourly = df.groupby('hour')['noise_level_db'].mean()
            top_hours = hourly.nlargest(5)
            for hour, avg in top_hours.items():
                peak_periods.append({'hour': int(hour), 'avg_noise': round(avg, 1)})

        # Top hotspots
        top_hotspots = self.get_hotspots(top_n=5)

        # Sensitive locations risk
        sensitive_risk = []
        for zone in Zone.get_all(self.db):
            if zone['zone_type'] in ('school', 'hospital'):
                zone_readings = NoiseReading.get_all(self.db, filters={'zone_id': zone['id']}, limit=5000)
                if zone_readings:
                    avg = round(np.mean([r['noise_level_db'] for r in zone_readings]), 1)
                    rule = NoiseLimitRule.get_by_zone_type(self.db, zone['zone_type'])
                    limit = rule['day_limit_db'] if rule else 50
                    v_count = Violation.get_count(self.db, filters={'zone_type': zone['zone_type']})
                    status = 'Safe' if avg < limit else 'At Risk' if avg < limit + 10 else 'Critical'
                    sensitive_risk.append({
                        'zone_name': zone['name'],
                        'zone_type': zone['zone_type'],
                        'avg_noise': avg,
                        'limit': limit,
                        'violation_count': v_count,
                        'status': status
                    })

        # Recommendations
        recommendations = self.get_recommendations(top_hotspots)

        # Summary text
        summary_text = (
            f"Analysis of {total_readings} noise readings reveals {total_violations} violations. "
            f"The most affected area is {most_affected[0]['zone_name'] if most_affected else 'N/A'} "
            f"with an average noise level of {most_affected[0]['mean'] if most_affected else 0} dB. "
            f"{len(sensitive_risk)} sensitive locations (schools/hospitals) are being monitored."
        )

        return {
            'total_readings': total_readings,
            'total_violations': total_violations,
            'most_affected_zones': most_affected,
            'peak_periods': peak_periods,
            'top_hotspots': top_hotspots,
            'sensitive_locations_risk': sensitive_risk,
            'recommendations': recommendations,
            'summary_text': summary_text
        }

