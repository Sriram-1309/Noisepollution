import unittest
import sys
import os

# Add project root directory to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from models.sensor import Sensor
from models.zone import Zone
from models.noise_limit_rule import NoiseLimitRule
from models.noise_reading import NoiseReading
from models.violation import Violation


class TestNoisePollutionModels(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database for test isolation
        self.db = DatabaseManager(':memory:')
        self.db.init_db()

    def test_zone_crud(self):
        zone_data = {
            'name': 'Gachibowli Tech Zone',
            'zone_type': 'commercial',
            'latitude': 17.4401,
            'longitude': 78.3489,
            'radius': 600,
            'description': 'IT office corridor'
        }
        zone_id = Zone.create(self.db, zone_data)
        self.assertIsNotNone(zone_id)
        self.assertGreater(zone_id, 0)

        zone = Zone.get_by_id(self.db, zone_id)
        self.assertIsNotNone(zone)
        self.assertEqual(zone['name'], 'Gachibowli Tech Zone')
        self.assertEqual(zone['zone_type'], 'commercial')

        # Test update
        updated = Zone.update(self.db, zone_id, {'name': 'Gachibowli Financial District'})
        self.assertTrue(updated)
        zone_updated = Zone.get_by_id(self.db, zone_id)
        self.assertEqual(zone_updated['name'], 'Gachibowli Financial District')

    def test_sensor_crud(self):
        zone_id = Zone.create(self.db, {
            'name': 'Jubilee Hills Silence Zone',
            'zone_type': 'silence',
            'latitude': 17.4325,
            'longitude': 78.4072
        })

        sensor_data = {
            'name': 'Jubilee Hills Sensor Alpha',
            'latitude': 17.4328,
            'longitude': 78.4075,
            'zone_id': zone_id,
            'status': 'online'
        }
        sensor_id = Sensor.create(self.db, sensor_data)
        self.assertIsNotNone(sensor_id)
        self.assertGreater(sensor_id, 0)

        sensor = Sensor.get_by_id(self.db, sensor_id)
        self.assertIsNotNone(sensor)
        self.assertEqual(sensor['name'], 'Jubilee Hills Sensor Alpha')
        self.assertEqual(sensor['zone_id'], zone_id)

        # Test count
        count = Sensor.get_count(self.db)
        self.assertEqual(count, 1)

        # Test update
        Sensor.update(self.db, sensor_id, {'status': 'offline'})
        sensor_offline = Sensor.get_by_id(self.db, sensor_id)
        self.assertEqual(sensor_offline['status'], 'offline')

        # Test delete
        deleted = Sensor.delete(self.db, sensor_id)
        self.assertTrue(deleted)
        self.assertIsNone(Sensor.get_by_id(self.db, sensor_id))

    def test_noise_limit_rule(self):
        rule_data = {
            'zone_type': 'residential',
            'day_limit_db': 55.0,
            'night_limit_db': 45.0,
            'day_start_hour': 6,
            'night_start_hour': 22,
            'description': 'Residential zone limits'
        }
        rule_id = NoiseLimitRule.create(self.db, rule_data)
        self.assertIsNotNone(rule_id)

        # Day limit check (e.g. 14:00)
        day_limit = NoiseLimitRule.get_applicable_limit_for_zone(self.db, 'residential', 14)
        self.assertEqual(day_limit, 55.0)

        # Night limit check (e.g. 23:00 and 03:00)
        night_limit_23 = NoiseLimitRule.get_applicable_limit_for_zone(self.db, 'residential', 23)
        self.assertEqual(night_limit_23, 45.0)

        night_limit_03 = NoiseLimitRule.get_applicable_limit_for_zone(self.db, 'residential', 3)
        self.assertEqual(night_limit_03, 45.0)

    def test_noise_reading_and_stats(self):
        sensor_id = Sensor.create(self.db, {
            'name': 'Test Sensor',
            'latitude': 17.3850,
            'longitude': 78.4867
        })

        readings = [
            {'sensor_id': sensor_id, 'timestamp': '2026-10-13T10:00:00', 'noise_level_db': 62.5, 'latitude': 17.3850, 'longitude': 78.4867, 'zone_id': 1},
            {'sensor_id': sensor_id, 'timestamp': '2026-10-13T11:00:00', 'noise_level_db': 74.0, 'latitude': 17.3850, 'longitude': 78.4867, 'zone_id': 1},
            {'sensor_id': sensor_id, 'timestamp': '2026-10-13T12:00:00', 'noise_level_db': 58.5, 'latitude': 17.3850, 'longitude': 78.4867, 'zone_id': 1}
        ]
        count = NoiseReading.create_batch(self.db, readings)
        self.assertEqual(count, 3)

        total = NoiseReading.get_count(self.db)
        self.assertEqual(total, 3)

        avg = NoiseReading.get_average(self.db)
        self.assertEqual(avg, 65.0)

        max_reading = NoiseReading.get_max(self.db)
        self.assertIsNotNone(max_reading)
        self.assertEqual(max_reading['noise_level_db'], 74.0)

    def test_violation_severity(self):
        self.assertEqual(Violation.get_severity(3.2), 'low')
        self.assertEqual(Violation.get_severity(12.5), 'medium')
        self.assertEqual(Violation.get_severity(18.0), 'high')
        self.assertEqual(Violation.get_severity(28.4), 'critical')


if __name__ == '__main__':
    unittest.main()

