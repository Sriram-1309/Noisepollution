"""
Sensor Data Simulator - Generates realistic simulated noise readings.
Creates demo zones, sensors, noise limit rules, and time-varying readings
for demonstration and testing purposes.
"""
import random
from datetime import datetime, timedelta
import numpy as np
from models.sensor import Sensor
from models.noise_reading import NoiseReading
from models.zone import Zone
from models.noise_limit_rule import NoiseLimitRule


class SensorDataSimulator:
    """Generates simulated sensor data for the Noise Pollution Mapping System.

    All generated data is clearly marked as simulated and is intended
    for demonstration and educational purposes only.
    """

    # Demo zones for Hyderabad, India
    DEMO_ZONES = [
        {'name': 'Banjara Hills Residential', 'zone_type': 'residential', 'latitude': 17.4156, 'longitude': 78.4347, 'radius': 600, 'description': 'Upscale residential area in central Hyderabad'},
        {'name': 'Ameerpet Commercial Hub', 'zone_type': 'commercial', 'latitude': 17.4375, 'longitude': 78.4483, 'radius': 500, 'description': 'Major commercial and coaching center hub'},
        {'name': 'Jeedimetla Industrial Area', 'zone_type': 'industrial', 'latitude': 17.4975, 'longitude': 78.4325, 'radius': 800, 'description': 'Industrial zone with manufacturing units'},
        {'name': 'Osmania General Hospital', 'zone_type': 'hospital', 'latitude': 17.3616, 'longitude': 78.4747, 'radius': 400, 'description': 'Major government hospital - silence zone'},
        {'name': 'NIMS Hospital', 'zone_type': 'hospital', 'latitude': 17.3950, 'longitude': 78.3927, 'radius': 400, 'description': 'Nizam Institute of Medical Sciences - silence zone'},
        {'name': 'Narayana School Abids', 'zone_type': 'school', 'latitude': 17.3925, 'longitude': 78.4753, 'radius': 350, 'description': 'School zone in Abids area'},
        {'name': 'Kendriya Vidyalaya Picket', 'zone_type': 'school', 'latitude': 17.4450, 'longitude': 78.5050, 'radius': 350, 'description': 'Central school in Secunderabad'},
        {'name': 'Mehdipatnam Traffic Junction', 'zone_type': 'traffic', 'latitude': 17.3950, 'longitude': 78.4400, 'radius': 500, 'description': 'Major traffic intersection'},
        {'name': 'Begum Bazaar Market', 'zone_type': 'commercial', 'latitude': 17.3775, 'longitude': 78.4736, 'radius': 450, 'description': 'Busy wholesale market area'},
        {'name': 'Jubilee Hills Silence Zone', 'zone_type': 'silence', 'latitude': 17.4325, 'longitude': 78.4072, 'radius': 500, 'description': 'Designated silence zone near institutions'},
        {'name': 'Kukatpally Housing Board', 'zone_type': 'residential', 'latitude': 17.4849, 'longitude': 78.3916, 'radius': 600, 'description': 'Large residential colony'},
        {'name': 'HITEC City Business District', 'zone_type': 'commercial', 'latitude': 17.4435, 'longitude': 78.3772, 'radius': 700, 'description': 'IT corridor and business district'},
    ]

    # Demo noise limits (inspired by CPCB guidelines - for demonstration only)
    DEMO_LIMITS = [
        {'zone_type': 'residential', 'day_limit_db': 55, 'night_limit_db': 45, 'description': 'Residential area limits (demo values inspired by CPCB)'},
        {'zone_type': 'commercial', 'day_limit_db': 65, 'night_limit_db': 55, 'description': 'Commercial area limits (demo values inspired by CPCB)'},
        {'zone_type': 'industrial', 'day_limit_db': 75, 'night_limit_db': 70, 'description': 'Industrial area limits (demo values inspired by CPCB)'},
        {'zone_type': 'silence', 'day_limit_db': 50, 'night_limit_db': 40, 'description': 'Silence zone limits (demo values inspired by CPCB)'},
        {'zone_type': 'school', 'day_limit_db': 50, 'night_limit_db': 40, 'description': 'School zone limits - treated as silence zone (demo)'},
        {'zone_type': 'hospital', 'day_limit_db': 50, 'night_limit_db': 40, 'description': 'Hospital zone limits - treated as silence zone (demo)'},
        {'zone_type': 'traffic', 'day_limit_db': 70, 'night_limit_db': 60, 'description': 'Traffic zone limits (demo values)'},
    ]

    # Base noise levels by zone type and time period [day_low, day_high, night_low, night_high]
    NOISE_PROFILES = {
        'residential': {'day': (42, 52), 'night': (30, 40)},
        'commercial':  {'day': (55, 65), 'night': (40, 50)},
        'industrial':  {'day': (65, 75), 'night': (55, 65)},
        'hospital':    {'day': (40, 50), 'night': (30, 35)},
        'school':      {'day': (40, 50), 'night': (30, 35)},
        'traffic':     {'day': (60, 72), 'night': (45, 55)},
        'silence':     {'day': (35, 45), 'night': (25, 35)},
    }

    def __init__(self, db_manager):
        self.db = db_manager

    def seed_initial_data(self):
        """Seed the database with demo zones, sensors, limits, and readings.

        This creates a complete demonstration dataset for Hyderabad.
        """
        print("[Simulator] Seeding initial demo data...")

        # Create zones
        zone_ids = {}
        for zone_data in self.DEMO_ZONES:
            zone_id = Zone.create(self.db, zone_data)
            zone_ids[zone_data['name']] = zone_id
        print(f"  Created {len(zone_ids)} zones")

        # Create noise limit rules
        for rule in self.DEMO_LIMITS:
            NoiseLimitRule.create(self.db, rule)
        print(f"  Created {len(self.DEMO_LIMITS)} noise limit rules")

        # Create sensors (2-3 per zone)
        sensor_count = 0
        zones = Zone.get_all(self.db)
        for zone in zones:
            num_sensors = random.randint(2, 3)
            for i in range(num_sensors):
                sensor_count += 1
                # Add small random offset from zone center
                lat_offset = random.uniform(-0.005, 0.005)
                lng_offset = random.uniform(-0.005, 0.005)
                sensor_data = {
                    'name': f"{zone['name']} Sensor {'ABCDE'[i]}",
                    'latitude': round(zone['latitude'] + lat_offset, 6),
                    'longitude': round(zone['longitude'] + lng_offset, 6),
                    'zone_id': zone['id'],
                    'status': 'online' if random.random() > 0.1 else 'offline'
                }
                Sensor.create(self.db, sensor_data)
        print(f"  Created {sensor_count} sensors")

        # Generate initial readings
        count = self.generate_readings(num_readings=500, hours_back=48)
        print(f"  Generated {count} noise readings")
        print("[Simulator] Seeding complete!")

    def get_noise_level_for_zone(self, zone_type, hour):
        """Calculate a realistic noise level based on zone type and time of day.

        Args:
            zone_type: Type of zone (residential, commercial, etc.)
            hour: Hour of day (0-23)

        Returns:
            float: Simulated noise level in dB
        """
        profile = self.NOISE_PROFILES.get(zone_type, self.NOISE_PROFILES['residential'])

        # Determine if it's day or night
        is_day = 6 <= hour < 22
        base_range = profile['day'] if is_day else profile['night']
        base = np.random.uniform(base_range[0], base_range[1])

        # Rush hour boost for traffic and commercial zones
        if zone_type in ('traffic', 'commercial'):
            if 7 <= hour <= 9:   # Morning rush
                base += np.random.uniform(5, 10)
            elif 17 <= hour <= 19:  # Evening rush
                base += np.random.uniform(5, 10)

        # School hours - extra noise during school time
        if zone_type == 'school' and 8 <= hour <= 15:
            base += np.random.uniform(3, 8)

        # Add Gaussian noise
        noise = np.random.normal(0, 3)
        level = base + noise

        # Occasional spikes (5% chance) to demonstrate violations
        if random.random() < 0.05:
            spike = np.random.uniform(15, 25)
            level += spike

        return round(max(20, min(level, 120)), 1)  # Clamp between 20-120 dB

    def generate_readings(self, num_readings=500, hours_back=48):
        """Generate simulated noise readings for all sensors.

        Args:
            num_readings: Approximate total number of readings to generate
            hours_back: How many hours of historical data to create

        Returns:
            int: Number of readings generated
        """
        sensors = Sensor.get_all(self.db)
        if not sensors:
            return 0

        readings = []
        now = datetime.now()
        readings_per_sensor = max(1, num_readings // len(sensors))

        for sensor in sensors:
            zone_type = sensor.get('zone_type', 'residential')
            for _ in range(readings_per_sensor):
                # Random timestamp within the window
                offset_hours = random.uniform(0, hours_back)
                ts = now - timedelta(hours=offset_hours)
                hour = ts.hour

                noise_level = self.get_noise_level_for_zone(zone_type, hour)

                readings.append({
                    'sensor_id': sensor['id'],
                    'timestamp': ts.isoformat(),
                    'noise_level_db': noise_level,
                    'latitude': sensor['latitude'],
                    'longitude': sensor['longitude'],
                    'zone_id': sensor.get('zone_id')
                })

        # Bulk insert
        if readings:
            NoiseReading.create_batch(self.db, readings)

        # Update sensor last_updated timestamps
        for sensor in sensors:
            Sensor.update(self.db, sensor['id'], {'status': sensor.get('status', 'online')})

        return len(readings)

    def reset_data(self):
        """Delete all readings and violations, keeping sensors and zones."""
        from models.violation import Violation
        Violation.delete_all(self.db)
        NoiseReading.delete_all(self.db)
        print("[Simulator] Readings and violations cleared.")

    def full_reset(self):
        """Delete everything and re-seed from scratch."""
        from models.violation import Violation
        Violation.delete_all(self.db)
        NoiseReading.delete_all(self.db)
        self.db.execute_update("DELETE FROM sensors")
        self.db.execute_update("DELETE FROM noise_limit_rules")
        self.db.execute_update("DELETE FROM zones")
        print("[Simulator] Full reset complete. Re-seeding...")
        self.seed_initial_data()

