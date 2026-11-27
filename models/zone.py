"""
Zone Model - Represents a geographic monitoring zone in the city.
"""


class Zone:
    """Represents a monitoring zone (residential, commercial, industrial, etc.)."""

    ZONE_TYPES = ['residential', 'commercial', 'industrial', 'silence', 'school', 'hospital', 'traffic']

    def __init__(self, id=None, name='', zone_type='', latitude=0.0,
                 longitude=0.0, radius=500.0, description=''):
        self.id = id
        self.name = name
        self.zone_type = zone_type
        self.latitude = latitude
        self.longitude = longitude
        self.radius = radius
        self.description = description

    def to_dict(self):
        """Convert zone to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'zone_type': self.zone_type,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'radius': self.radius,
            'description': self.description
        }

    @staticmethod
    def get_all(db_manager):
        """Retrieve all zones with sensor count."""
        query = '''
            SELECT z.*,
                   (SELECT COUNT(*) FROM sensors s WHERE s.zone_id = z.id) as sensor_count
            FROM zones z
            ORDER BY z.id
        '''
        return db_manager.execute_query(query)

    @staticmethod
    def get_by_id(db_manager, zone_id):
        """Retrieve a zone by ID."""
        query = 'SELECT * FROM zones WHERE id = ?'
        results = db_manager.execute_query(query, (zone_id,))
        return results[0] if results else None

    @staticmethod
    def get_by_type(db_manager, zone_type):
        """Retrieve all zones of a specific type."""
        query = 'SELECT * FROM zones WHERE zone_type = ? ORDER BY name'
        return db_manager.execute_query(query, (zone_type,))

    @staticmethod
    def create(db_manager, data):
        """Create a new zone."""
        query = '''
            INSERT INTO zones (name, zone_type, latitude, longitude, radius, description)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        params = (
            data.get('name', ''),
            data.get('zone_type', ''),
            data.get('latitude', 0.0),
            data.get('longitude', 0.0),
            data.get('radius', 500.0),
            data.get('description', '')
        )
        return db_manager.execute_insert(query, params)

    @staticmethod
    def update(db_manager, zone_id, data):
        """Update zone details."""
        fields = []
        params = []
        for key in ['name', 'zone_type', 'latitude', 'longitude', 'radius', 'description']:
            if key in data:
                fields.append(f"{key} = ?")
                params.append(data[key])
        if not fields:
            return False
        params.append(zone_id)
        query = f"UPDATE zones SET {', '.join(fields)} WHERE id = ?"
        return db_manager.execute_update(query, params) > 0

    @staticmethod
    def delete(db_manager, zone_id):
        """Delete a zone."""
        # Unlink sensors from this zone
        db_manager.execute_update("UPDATE sensors SET zone_id = NULL WHERE zone_id = ?", (zone_id,))
        return db_manager.execute_update("DELETE FROM zones WHERE id = ?", (zone_id,)) > 0

