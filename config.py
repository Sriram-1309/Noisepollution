"""
Configuration settings for the Noise Pollution Mapping System.
"""
import os
import secrets

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'noise_pollution.db')

# Flask
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or secrets.token_hex(32)
DEBUG = os.environ.get('FLASK_DEBUG', '').lower() == 'true'

# Map defaults (Hyderabad, India)
DEFAULT_CITY_CENTER = (17.385, 78.4867)
DEFAULT_ZOOM = 12

# Noise level color coding
NOISE_COLORS = {
    'low': '#28a745',
    'moderate': '#ffc107',
    'high': '#fd7e14',
    'very_high': '#dc3545'
}

# Noise thresholds in dB
NOISE_THRESHOLDS = {
    'low': (0, 55),
    'moderate': (55, 65),
    'high': (65, 75),
    'very_high': (75, 200)
}

