"""
NoiseLimitRule Model - Defines permissible noise limits per zone type.
Supports different limits for day and night periods.
"""


class NoiseLimitRule:
    """Defines noise limit rules for different zone types with day/night variation."""

    def __init__(self, id=None, zone_type='', day_limit_db=0.0, night_limit_db=0.0,
                 day_start_hour=6, night_start_hour=22, description=''):
        self.id = id
        self.zone_type = zone_type
        self.day_limit_db = day_limit_db
        self.night_limit_db = night_limit_db
        self.day_start_hour = day_start_hour
        self.night_start_hour = night_start_hour
        self.description = description

    def to_dict(self):
        """Convert rule to dictionary."""
        return {
            'id': self.id,
            'zone_type': self.zone_type,
            'day_limit_db': self.day_limit_db,
            'night_limit_db': self.night_limit_db,
            'day_start_hour': self.day_start_hour,
            'night_start_hour': self.night_start_hour,
            'description': self.description
        }

    def get_applicable_limit(self, hour):
        """Return the applicable noise limit based on the hour of day.

        Args:
            hour: Hour of day (0-23)

        Returns:
            float: Applicable noise limit in dB
        """
        if self.day_start_hour <= hour < self.night_start_hour:
            return self.day_limit_db
        return self.night_limit_db

    @staticmethod
    def get_all(db_manager):
        """Retrieve all noise limit rules."""
        return db_manager.execute_query("SELECT * FROM noise_limit_rules ORDER BY zone_type")

    @staticmethod
    def get_by_zone_type(db_manager, zone_type):
        """Retrieve rule for a specific zone type."""
        results = db_manager.execute_query(
            "SELECT * FROM noise_limit_rules WHERE zone_type = ?", (zone_type,)
        )
        return results[0] if results else None

    @staticmethod
    def create(db_manager, data):
        """Create a new noise limit rule."""
        query = '''
            INSERT INTO noise_limit_rules (zone_type, day_limit_db, night_limit_db,
                                           day_start_hour, night_start_hour, description)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        params = (
            data.get('zone_type', ''),
            data.get('day_limit_db', 0.0),
            data.get('night_limit_db', 0.0),
            data.get('day_start_hour', 6),
            data.get('night_start_hour', 22),
            data.get('description', '')
        )
        return db_manager.execute_insert(query, params)

    @staticmethod
    def update(db_manager, rule_id, data):
        """Update a noise limit rule."""
        fields = []
        params = []
        for key in ['zone_type', 'day_limit_db', 'night_limit_db',
                     'day_start_hour', 'night_start_hour', 'description']:
            if key in data:
                fields.append(f"{key} = ?")
                params.append(data[key])
        if not fields:
            return False
        params.append(rule_id)
        query = f"UPDATE noise_limit_rules SET {', '.join(fields)} WHERE id = ?"
        return db_manager.execute_update(query, params) > 0

    @staticmethod
    def delete(db_manager, rule_id):
        """Delete a noise limit rule."""
        return db_manager.execute_update("DELETE FROM noise_limit_rules WHERE id = ?", (rule_id,)) > 0

    @staticmethod
    def get_applicable_limit_for_zone(db_manager, zone_type, hour):
        """Get the applicable noise limit for a zone type at a given hour.

        Returns:
            float: The applicable dB limit, or 75.0 as fallback
        """
        rule_data = NoiseLimitRule.get_by_zone_type(db_manager, zone_type)
        if not rule_data:
            return 75.0  # Default fallback
        rule = NoiseLimitRule(
            day_limit_db=rule_data['day_limit_db'],
            night_limit_db=rule_data['night_limit_db'],
            day_start_hour=rule_data['day_start_hour'],
            night_start_hour=rule_data['night_start_hour']
        )
        return rule.get_applicable_limit(hour)

