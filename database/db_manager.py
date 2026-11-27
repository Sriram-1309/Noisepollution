"""
Database Manager - Handles all SQLite database operations.
Provides connection management and CRUD utilities.
"""
import sqlite3
import os


class DatabaseManager:
    """Manages SQLite database connections and operations."""

    def __init__(self, db_path=None):
        """Initialize database manager with path to SQLite file."""
        if db_path == ':memory:':
            self.db_path = ':memory:'
        else:
            if db_path is None:
                from config import DATABASE_PATH
                self.db_path = DATABASE_PATH
            else:
                self.db_path = db_path
            # Create directory if it doesn't exist
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)

    def get_connection(self):
        """Get a database connection with Row factory for dict-like access."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        """Create all database tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS zones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                zone_type TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                radius REAL DEFAULT 500,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS sensors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                zone_id INTEGER,
                status TEXT DEFAULT 'online',
                installed_date TEXT,
                last_updated TEXT,
                FOREIGN KEY (zone_id) REFERENCES zones(id)
            );

            CREATE TABLE IF NOT EXISTS noise_limit_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zone_type TEXT NOT NULL UNIQUE,
                day_limit_db REAL NOT NULL,
                night_limit_db REAL NOT NULL,
                day_start_hour INTEGER DEFAULT 6,
                night_start_hour INTEGER DEFAULT 22,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS noise_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                noise_level_db REAL NOT NULL,
                latitude REAL,
                longitude REAL,
                zone_id INTEGER,
                FOREIGN KEY (sensor_id) REFERENCES sensors(id),
                FOREIGN KEY (zone_id) REFERENCES zones(id)
            );

            CREATE TABLE IF NOT EXISTS violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reading_id INTEGER,
                sensor_id INTEGER NOT NULL,
                zone_id INTEGER,
                timestamp TEXT NOT NULL,
                noise_level_db REAL NOT NULL,
                applicable_limit_db REAL NOT NULL,
                exceedance_db REAL NOT NULL,
                zone_type TEXT,
                severity TEXT,
                location_name TEXT,
                latitude REAL,
                longitude REAL,
                FOREIGN KEY (reading_id) REFERENCES noise_readings(id),
                FOREIGN KEY (sensor_id) REFERENCES sensors(id),
                FOREIGN KEY (zone_id) REFERENCES zones(id)
            );

            CREATE INDEX IF NOT EXISTS idx_readings_sensor ON noise_readings(sensor_id);
            CREATE INDEX IF NOT EXISTS idx_readings_timestamp ON noise_readings(timestamp);
            CREATE INDEX IF NOT EXISTS idx_readings_zone ON noise_readings(zone_id);
            CREATE INDEX IF NOT EXISTS idx_violations_sensor ON violations(sensor_id);
            CREATE INDEX IF NOT EXISTS idx_violations_timestamp ON violations(timestamp);
            CREATE INDEX IF NOT EXISTS idx_violations_zone ON violations(zone_id);
        ''')

        conn.commit()
        conn.close()

    def execute_query(self, query, params=()):
        """Execute a SELECT query and return list of dicts."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Query error: {e}")
            return []
        finally:
            conn.close()

    def execute_insert(self, query, params=()):
        """Execute an INSERT query and return the last row id."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Insert error: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def execute_update(self, query, params=()):
        """Execute an UPDATE/DELETE query and return affected row count."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Update error: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()

    def execute_many(self, query, params_list):
        """Execute a query with many parameter sets (bulk insert)."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Bulk execute error: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()

    def close(self):
        """Placeholder for cleanup if needed."""
        pass

