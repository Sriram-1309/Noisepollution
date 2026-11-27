"""
NoiseReading Model - Represents a single noise measurement from a sensor.
"""
from datetime import datetime


class NoiseReading:
    """Represents a noise level reading taken by a sensor at a specific time."""

    def __init__(self, id=None, sensor_id=None, timestamp=None,
                 noise_level_db=0.0, latitude=0.0, longitude=0.0, zone_id=None):
        self.id = id
        self.sensor_id = sensor_id
        self.timestamp = timestamp or datetime.now().isoformat()
        self.noise_level_db = noise_level_db
        self.latitude = latitude
        self.longitude = longitude
        self.zone_id = zone_id

    def to_dict(self):
        """Convert reading to dictionary."""
        return {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'timestamp': self.timestamp,
            'noise_level_db': self.noise_level_db,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'zone_id': self.zone_id
        }

    @staticmethod
    def create(db_manager, data):
        """Create a single noise reading."""
        query = '''
            INSERT INTO noise_readings (sensor_id, timestamp, noise_level_db, latitude, longitude, zone_id)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        params = (
            data.get('sensor_id'),
            data.get('timestamp', datetime.now().isoformat()),
            data.get('noise_level_db', 0.0),
            data.get('latitude', 0.0),
            data.get('longitude', 0.0),
            data.get('zone_id')
        )
        return db_manager.execute_insert(query, params)

    @staticmethod
    def create_batch(db_manager, readings):
        """Bulk insert noise readings. Returns count inserted."""
        query = '''
            INSERT INTO noise_readings (sensor_id, timestamp, noise_level_db, latitude, longitude, zone_id)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        params_list = [
            (r.get('sensor_id'), r.get('timestamp'), r.get('noise_level_db'),
             r.get('latitude'), r.get('longitude'), r.get('zone_id'))
            for r in readings
        ]
        return db_manager.execute_many(query, params_list)

    @staticmethod
    def get_all(db_manager, filters=None, limit=1000):
        """Get readings with optional filters."""
        query = '''
            SELECT nr.*, s.name as sensor_name, z.zone_type, z.name as zone_name
            FROM noise_readings nr
            LEFT JOIN sensors s ON nr.sensor_id = s.id
            LEFT JOIN zones z ON nr.zone_id = z.id
            WHERE 1=1
        '''
        params = []
        if filters:
            if filters.get('sensor_id'):
                query += " AND nr.sensor_id = ?"
                params.append(int(filters['sensor_id']))
            if filters.get('zone_id'):
                query += " AND nr.zone_id = ?"
                params.append(int(filters['zone_id']))
            if filters.get('zone_type'):
                query += " AND z.zone_type = ?"
                params.append(filters['zone_type'])
            if filters.get('min_db'):
                query += " AND nr.noise_level_db >= ?"
                params.append(float(filters['min_db']))
            if filters.get('max_db'):
                query += " AND nr.noise_level_db <= ?"
                params.append(float(filters['max_db']))
            if filters.get('start_date'):
                query += " AND nr.timestamp >= ?"
                params.append(filters['start_date'])
            if filters.get('end_date'):
                query += " AND nr.timestamp <= ?"
                params.append(filters['end_date'])

        query += f" ORDER BY nr.timestamp DESC LIMIT ?"
        params.append(limit)
        return db_manager.execute_query(query, params)

    @staticmethod
    def get_by_sensor(db_manager, sensor_id, limit=100):
        """Get readings for a specific sensor."""
        query = '''
            SELECT * FROM noise_readings
            WHERE sensor_id = ?
            ORDER BY timestamp DESC LIMIT ?
        '''
        return db_manager.execute_query(query, (sensor_id, limit))

    @staticmethod
    def get_latest_by_sensor(db_manager, sensor_id):
        """Get the most recent reading for a sensor."""
        query = '''
            SELECT * FROM noise_readings
            WHERE sensor_id = ?
            ORDER BY timestamp DESC LIMIT 1
        '''
        results = db_manager.execute_query(query, (sensor_id,))
        return results[0] if results else None

    @staticmethod
    def get_count(db_manager):
        """Get total number of readings."""
        result = db_manager.execute_query("SELECT COUNT(*) as count FROM noise_readings")
        return result[0]['count'] if result else 0

    @staticmethod
    def get_average(db_manager):
        """Get average noise level across all readings."""
        result = db_manager.execute_query(
            "SELECT AVG(noise_level_db) as avg_db FROM noise_readings"
        )
        return round(result[0]['avg_db'], 1) if result and result[0]['avg_db'] else 0.0

    @staticmethod
    def get_max(db_manager):
        """Get the highest noise reading with sensor info."""
        query = '''
            SELECT nr.*, s.name as sensor_name, z.name as zone_name
            FROM noise_readings nr
            LEFT JOIN sensors s ON nr.sensor_id = s.id
            LEFT JOIN zones z ON nr.zone_id = z.id
            ORDER BY nr.noise_level_db DESC
            LIMIT 1
        '''
        results = db_manager.execute_query(query)
        return results[0] if results else None

    @staticmethod
    def delete_all(db_manager):
        """Delete all readings."""
        return db_manager.execute_update("DELETE FROM noise_readings")

