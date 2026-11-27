"""
Violation Model - Represents a noise limit violation event.
"""


class Violation:
    """Records when a noise reading exceeds the permissible limit for its zone."""

    def __init__(self, id=None, reading_id=None, sensor_id=None, zone_id=None,
                 timestamp=None, noise_level_db=0.0, applicable_limit_db=0.0,
                 exceedance_db=0.0, zone_type='', severity='', location_name='',
                 latitude=0.0, longitude=0.0):
        self.id = id
        self.reading_id = reading_id
        self.sensor_id = sensor_id
        self.zone_id = zone_id
        self.timestamp = timestamp
        self.noise_level_db = noise_level_db
        self.applicable_limit_db = applicable_limit_db
        self.exceedance_db = exceedance_db
        self.zone_type = zone_type
        self.severity = severity
        self.location_name = location_name
        self.latitude = latitude
        self.longitude = longitude

    def to_dict(self):
        """Convert violation to dictionary."""
        return {
            'id': self.id, 'reading_id': self.reading_id,
            'sensor_id': self.sensor_id, 'zone_id': self.zone_id,
            'timestamp': self.timestamp, 'noise_level_db': self.noise_level_db,
            'applicable_limit_db': self.applicable_limit_db,
            'exceedance_db': self.exceedance_db, 'zone_type': self.zone_type,
            'severity': self.severity, 'location_name': self.location_name,
            'latitude': self.latitude, 'longitude': self.longitude
        }

    @staticmethod
    def get_severity(exceedance_db):
        """Determine severity based on how much the limit was exceeded.

        Args:
            exceedance_db: Amount of exceedance in dB

        Returns:
            str: 'low', 'medium', 'high', or 'critical'
        """
        if exceedance_db < 5:
            return 'low'
        elif exceedance_db < 15:
            return 'medium'
        elif exceedance_db < 25:
            return 'high'
        return 'critical'

    @staticmethod
    def create(db_manager, data):
        """Create a violation record."""
        query = '''
            INSERT INTO violations (reading_id, sensor_id, zone_id, timestamp,
                                    noise_level_db, applicable_limit_db, exceedance_db,
                                    zone_type, severity, location_name, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            data.get('reading_id'), data.get('sensor_id'), data.get('zone_id'),
            data.get('timestamp'), data.get('noise_level_db'),
            data.get('applicable_limit_db'), data.get('exceedance_db'),
            data.get('zone_type', ''), data.get('severity', ''),
            data.get('location_name', ''), data.get('latitude', 0.0),
            data.get('longitude', 0.0)
        )
        return db_manager.execute_insert(query, params)

    @staticmethod
    def get_all(db_manager, filters=None, limit=500):
        """Get violations with optional filters and sensor name join."""
        query = '''
            SELECT v.*, s.name as sensor_name
            FROM violations v
            LEFT JOIN sensors s ON v.sensor_id = s.id
            WHERE 1=1
        '''
        params = []
        if filters:
            if filters.get('zone_type'):
                query += " AND v.zone_type = ?"
                params.append(filters['zone_type'])
            if filters.get('severity'):
                query += " AND v.severity = ?"
                params.append(filters['severity'])
            if filters.get('start_date'):
                query += " AND v.timestamp >= ?"
                params.append(filters['start_date'])
            if filters.get('end_date'):
                query += " AND v.timestamp <= ?"
                params.append(filters['end_date'])
            if filters.get('sensor_id'):
                query += " AND v.sensor_id = ?"
                params.append(int(filters['sensor_id']))
        query += f" ORDER BY v.timestamp DESC LIMIT ?"
        params.append(limit)
        return db_manager.execute_query(query, params)

    @staticmethod
    def get_by_id(db_manager, violation_id):
        """Get a single violation with full details."""
        query = '''
            SELECT v.*, s.name as sensor_name, z.name as zone_name
            FROM violations v
            LEFT JOIN sensors s ON v.sensor_id = s.id
            LEFT JOIN zones z ON v.zone_id = z.id
            WHERE v.id = ?
        '''
        results = db_manager.execute_query(query, (violation_id,))
        return results[0] if results else None

    @staticmethod
    def get_count(db_manager, filters=None):
        """Get count of violations with optional filters."""
        query = "SELECT COUNT(*) as count FROM violations WHERE 1=1"
        params = []
        if filters:
            if filters.get('zone_type'):
                query += " AND zone_type = ?"
                params.append(filters['zone_type'])
            if filters.get('severity'):
                query += " AND severity = ?"
                params.append(filters['severity'])
            if filters.get('start_date'):
                query += " AND timestamp >= ?"
                params.append(filters['start_date'])
            if filters.get('end_date'):
                query += " AND timestamp <= ?"
                params.append(filters['end_date'])
        result = db_manager.execute_query(query, params)
        return result[0]['count'] if result else 0

    @staticmethod
    def delete_all(db_manager):
        """Delete all violations."""
        return db_manager.execute_update("DELETE FROM violations")

