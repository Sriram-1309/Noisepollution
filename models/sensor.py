"""
Sensor Model - Represents a noise monitoring sensor device.
Uses OOP with static methods for database CRUD operations.
"""
from datetime import datetime


class Sensor:
    """Represents a noise monitoring sensor deployed in the city."""

    def __init__(self, id=None, name='', latitude=0.0, longitude=0.0,
                 zone_id=None, status='online', installed_date=None, last_updated=None):
        self.id = id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.zone_id = zone_id
        self.status = status
        self.installed_date = installed_date or datetime.now().isoformat()
        self.last_updated = last_updated or datetime.now().isoformat()

    def to_dict(self):
        """Convert sensor to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'zone_id': self.zone_id,
            'status': self.status,
            'installed_date': self.installed_date,
            'last_updated': self.last_updated
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Sensor instance from a dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            latitude=data.get('latitude', 0.0),
            longitude=data.get('longitude', 0.0),
            zone_id=data.get('zone_id'),
            status=data.get('status', 'online'),
            installed_date=data.get('installed_date'),
            last_updated=data.get('last_updated')
        )

    @staticmethod
    def get_all(db_manager):
        """Retrieve all sensors with zone information."""
        query = '''
            SELECT s.*, z.name as zone_name, z.zone_type
            FROM sensors s
            LEFT JOIN zones z ON s.zone_id = z.id
            ORDER BY s.id
        '''
        return db_manager.execute_query(query)

    @staticmethod
    def get_by_id(db_manager, sensor_id):
        """Retrieve a single sensor by ID with zone info."""
        query = '''
            SELECT s.*, z.name as zone_name, z.zone_type
            FROM sensors s
            LEFT JOIN zones z ON s.zone_id = z.id
            WHERE s.id = ?
        '''
        results = db_manager.execute_query(query, (sensor_id,))
        return results[0] if results else None

    @staticmethod
    def create(db_manager, data):
        """Create a new sensor and return its ID."""
        query = '''
            INSERT INTO sensors (name, latitude, longitude, zone_id, status, installed_date, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        now = datetime.now().isoformat()
        params = (
            data.get('name', ''),
            data.get('latitude', 0.0),
            data.get('longitude', 0.0),
            data.get('zone_id'),
            data.get('status', 'online'),
            data.get('installed_date', now),
            now
        )
        return db_manager.execute_insert(query, params)

    @staticmethod
    def update(db_manager, sensor_id, data):
        """Update sensor details."""
        fields = []
        params = []
        for key in ['name', 'latitude', 'longitude', 'zone_id', 'status']:
            if key in data:
                fields.append(f"{key} = ?")
                params.append(data[key])
        if not fields:
            return False
        fields.append("last_updated = ?")
        params.append(datetime.now().isoformat())
        params.append(sensor_id)
        query = f"UPDATE sensors SET {', '.join(fields)} WHERE id = ?"
        return db_manager.execute_update(query, params) > 0

    @staticmethod
    def delete(db_manager, sensor_id):
        """Delete a sensor by ID."""
        # Delete related readings and violations first
        db_manager.execute_update("DELETE FROM violations WHERE sensor_id = ?", (sensor_id,))
        db_manager.execute_update("DELETE FROM noise_readings WHERE sensor_id = ?", (sensor_id,))
        return db_manager.execute_update("DELETE FROM sensors WHERE id = ?", (sensor_id,)) > 0

    @staticmethod
    def get_count(db_manager):
        """Get total number of sensors."""
        result = db_manager.execute_query("SELECT COUNT(*) as count FROM sensors")
        return result[0]['count'] if result else 0

    @staticmethod
    def get_readings(db_manager, sensor_id, limit=100):
        """Get recent readings for a sensor."""
        query = '''
            SELECT * FROM noise_readings
            WHERE sensor_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        '''
        return db_manager.execute_query(query, (sensor_id, limit))

