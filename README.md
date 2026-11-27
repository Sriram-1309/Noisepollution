# 📢 Noise Pollution Intelligence Dashboard

**Noise Pollution Mapping System** — A full-stack urban environmental analytics dashboard and interactive spatial mapping platform for monitoring, analyzing, and detecting noise pollution violations across a metropolitan city.

> *"Monitor noise. Detect hotspots. Build quieter cities."*

---

## 📋 Table of Contents
1. [Overview & Problem Statement](#-overview--problem-statement)
2. [Key Features](#-key-features)
3. [Technology Stack](#-technology-stack)
4. [System Architecture & OOP Design](#-system-architecture--oop-design)
5. [Project Structure](#-project-structure)
6. [Step-by-Step Setup Guide (Windows & VS Code)](#-step-by-step-setup-guide-windows--vs-code)
7. [Application Modules & Usage Walkthrough](#-application-modules--usage-walkthrough)
8. [REST API Documentation](#-rest-api-documentation)
9. [Statistical Analysis & Hotspot Detection Logic](#-statistical-analysis--hotspot-detection-logic)
10. [Troubleshooting & Viva FAQs](#-troubleshooting--viva-faqs)

---

## 🎯 Overview & Problem Statement

Urban noise pollution poses severe risks to public health, cognitive development in schools, and patient recovery in hospitals. Municipal corporations and pollution control boards frequently face challenges in:
- Synthesizing large volumes of distributed acoustic measurements.
- Real-time detection of noise limit violations across different land-use categories (Silence zones, Residential, Commercial, Industrial, Traffic corridors).
- Discerning chronic violation hotspots from isolated, non-recurrent acoustic spikes.
- Visualizing spatial heatmaps to direct noise mitigation interventions (sound barriers, traffic rerouting, no-honking enforcement).

The **Noise Pollution Intelligence Dashboard** provides an end-to-end software solution featuring:
- Spatial heatmap generation using OpenStreetMap and Leaflet.js.
- Automated violation detection against day/night permissible thresholds.
- Time-series noise analytics utilizing Pandas and NumPy.
- Comprehensive reporting with CSV data export.
- Object-Oriented Programming (OOP) modeling for extensible real-world sensor integration.

*Note: For demonstration and educational purposes, the system comes pre-configured with 12 zones and 30 sensors across Hyderabad, India, driven by a realistic stochastic sensor simulator with diurnal variations, rush-hour peaks, and anomaly spikes.*

---

## ✨ Key Features

- **📊 Comprehensive Executive Dashboard**: 6 real-time KPI cards (Active Sensors, Average Noise, Violations, Monitored Sensitive Zones, Max Noise, and System Risk Level), live 24-hour trend line chart, zone distribution doughnut chart, recent activity feed, and interactive mini-map.
- **🗺️ Interactive Noise Map & Spatial Heatmap**: Dual-layer GIS mapping powered by Leaflet.js and Leaflet.heat with color-coded markers (Green, Yellow, Orange, Red), customizable filters (zone type, noise range), and detailed sensor popups with violation badges.
- **📡 Complete Sensor Lifecycle Management**: Searchable and sortable CRUD table, online/offline status tracking, geographic coordinates, and historical reading inspection with integrated Chart.js trendlines.
- **🏙️ Land-Use Zone Management**: Configurable monitoring zones (Residential, Commercial, Industrial, Silence, School, Hospital, Traffic) with metadata, spatial radius, and sensor bindings.
- **⚠️ Automated Violation Engine**: Evaluates noise measurements against time-of-day specific thresholds (day vs. night), determines exceedance in decibels, assigns severity ratings (`low`, `medium`, `high`, `critical`), and prioritizes sensitive educational and medical facilities.
- **📈 Advanced Time-Series Analytics**: Hourly trend distributions, 7-day moving averages, comparative cross-zone bar charts, peak noise hour rankers, and target compliance charts for schools and hospitals.
- **🔥 Statistical Hotspot Detection**: Weighted multi-factor scoring formula that penalizes chronic violation patterns and variance rather than transient noise peaks. Produces prioritized mitigation recommendations.
- **📑 Reports & Data Export Engine**: Configurable date-range reporting summaries with instant CSV exports for raw acoustic logs and violation registries, plus print-ready stylesheets.
- **⚙️ Dynamic Regulatory Settings**: Configurable day/night decibel thresholds, active observation windows, one-click dataset generators, and database reset/re-seed controls.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
|---|---|
| **Frontend UI / UX** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Font Awesome 6.5, Google Inter Font |
| **Mapping Engine** | Leaflet.js 1.9.4, Leaflet.heat plugin, OpenStreetMap Cartography |
| **Data Visualizations** | Chart.js 4.4.1 (Responsive Line, Bar, and Doughnut Charts) |
| **Backend Web Server** | Python 3, Flask 3.0 (Modular Blueprints architecture) |
| **Data Science & Stats** | Pandas 2.1, NumPy 1.26, SciPy 1.11 |
| **Database & Persistence** | SQLite3 (Foreign Keys enabled, Composite B-Tree Indexes) |
| **Testing** | Python `unittest` framework with in-memory SQLite isolation |

---

## 🏛️ System Architecture & OOP Design

The backend is built around clean Object-Oriented Programming (OOP) paradigms with strong separation of concerns:

```
                          ┌────────────────────────┐
                          │   Flask API & Routes   │
                          └───────────┬────────────┘
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            │                         │                         │
            ▼                         ▼                         ▼
   ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
   │  NoiseAnalyzer  │       │ HotspotDetector │       │ SensorSimulator │
   └────────┬────────┘       └────────┬────────┘       └────────┬────────┘
            │                         │                         │
            └─────────────────────────┼─────────────────────────┘
                                      │
                                      ▼
               ┌──────────────────────────────────────────────┐
               │              Domain OOP Models               │
               │  - Sensor              - NoiseLimitRule      │
               │  - Zone                - Violation           │
               │  - NoiseReading                              │
               └──────────────────────┬───────────────────────┘
                                      │
                                      ▼
               ┌──────────────────────────────────────────────┐
               │          DatabaseManager (SQLite3)           │
               └──────────────────────────────────────────────┘
```

### OOP Classes Summary:
1. `DatabaseManager` (`database/db_manager.py`): Manages thread-safe SQLite connection handles, executes parameterized SQL queries, performs batch inserts, and enforces database integrity.
2. `Sensor` (`models/sensor.py`): Models acoustic telemetry devices, coordinates, zone associations, and health status.
3. `NoiseReading` (`models/noise_reading.py`): Models discrete acoustic sensor samples with decibel measurements and timestamps.
4. `Zone` (`models/zone.py`): Represents bounded spatial zones with assigned land-use classifications.
5. `NoiseLimitRule` (`models/noise_limit_rule.py`): Encapsulates regulatory noise ceilings, supporting distinct daytime (06:00–22:00) and nighttime (22:00–06:00) limits.
6. `Violation` (`models/violation.py`): Represents verified regulatory breach instances with decibel delta calculations and tiered severity grades.
7. `SensorDataSimulator` (`services/simulator.py`): Generates realistic urban acoustic patterns incorporating diurnal curves, rush-hour impulses, and random anomalies.
8. `NoiseAnalyzer` (`services/noise_analyzer.py`): Leverages Pandas DataFrame aggregations to evaluate trends, peak hours, and rule evaluations.
9. `HotspotDetector` (`services/hotspot_detector.py`): Applies statistical formulations (mean, median, standard deviation, percentile ranks) and composite scoring to identify hotspots.

---

## 📁 Project Structure

```
Noisepollution/
│
├── app.py                       # Main Flask Application & Factory
├── config.py                    # Global App Configuration & Thresholds
├── requirements.txt             # Python Dependencies
├── README.md                    # System Documentation & Setup Guide
│
├── database/
│   ├── __init__.py
│   ├── db_manager.py            # SQLite Connection & Query Utility
│   └── noise_pollution.db      # SQLite Database File (Created automatically)
│
├── models/                      # Object-Oriented Domain Entities
│   ├── __init__.py
│   ├── sensor.py                # Sensor OOP Model
│   ├── noise_reading.py         # NoiseReading Model & Batch Operations
│   ├── zone.py                  # Zone Entity & Spatial Associations
│   ├── noise_limit_rule.py      # Noise Limits & Temporal Rules Engine
│   └── violation.py             # Violation Model & Severity Evaluator
│
├── services/                    # Business Logic & Data Science Services
│   ├── __init__.py
│   ├── simulator.py             # Stochastic Noise Telemetry Generator
│   ├── noise_analyzer.py        # Pandas Analytics & Violation Engine
│   └── hotspot_detector.py      # Statistical Hotspot Scoring & Diagnostics
│
├── routes/                      # Modular Flask Blueprints (REST Endpoints)
│   ├── __init__.py
│   ├── dashboard.py             # Dashboard Metrics Route
│   ├── sensors.py               # Sensor CRUD & History Routes
│   ├── zones.py                 # Zone Management Routes
│   ├── analytics.py             # Time-Series Data Routes
│   ├── violations.py            # Violation Inspection & Detection Routes
│   ├── reports.py               # Analytical Reports & CSV Streaming
│   └── settings.py              # Regulatory Limit Rules & Hotspots API
│
├── templates/                   # Jinja2 Modern UI Templates
│   ├── base.html                # Navigation Shell, Theme & Mobile Drawer
│   ├── dashboard.html           # KPI Summary & Overview Page
│   ├── map.html                 # Leaflet GIS Map & Heatmap
│   ├── sensors.html             # Sensor Registry & Modals
│   ├── zones.html               # Zone Directory Cards & Modal
│   ├── violations.html          # Violation Audit Table & Detail Modal
│   ├── analytics.html           # Time-Series Charts
│   ├── hotspots.html            # Hotspot Rankings & Spatial Buffer Map
│   ├── reports.html             # Printable Summary & CSV Downloads
│   └── settings.html            # Regulatory Limits & Simulation Console
│
├── static/                      # Static Assets
│   ├── css/
│   │   └── style.css            # Dark Navy & Professional Environmental UI
│   ├── js/                      # Dedicated Page JavaScript Controllers
│   │   ├── dashboard.js
│   │   ├── map.js
│   │   ├── sensors.js
│   │   ├── zones.js
│   │   ├── violations.js
│   │   ├── analytics.js
│   │   ├── hotspots.js
│   │   ├── reports.js
│   │   └── settings.js
│   └── images/
│       └── .gitkeep
│
└── tests/                       # Unit Testing Suite
    ├── __init__.py
    └── test_models.py           # Automated Test Suite for OOP Models
```

---

## 🚀 Step-by-Step Setup Guide (Windows & VS Code)

### Prerequisites
1. **Python 3.8+** installed ([python.org](https://www.python.org/downloads/)). *Be sure to check "Add Python to PATH" during installation.*
2. **Visual Studio Code** ([code.visualstudio.com](https://code.visualstudio.com/)).

### Step 1: Open the Project in VS Code
Open VS Code, press `Ctrl + K, Ctrl + O` (Open Folder), and select:
```
C:\Users\Kapu\Desktop\Noisepollution
```
Or open via command prompt / PowerShell:
```powershell
code C:\Users\Kapu\Desktop\Noisepollution
```

### Step 2: Open VS Code Integrated Terminal
Press `Ctrl + ~` (or select **Terminal** -> **New Terminal** from the menu).

### Step 3: Create a Virtual Environment
```powershell
python -m venv venv
```

### Step 4: Activate the Virtual Environment
- **On PowerShell:**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
  *(If you encounter a script execution restriction, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`, then run the command again).*

- **On Command Prompt (cmd):**
  ```cmd
  venv\Scripts\activate.bat
  ```

### Step 5: Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### Step 6: Verify with Unit Tests
Ensure all domain entities and in-memory database operations function as expected:
```powershell
python -m unittest tests/test_models.py
```
*Expected output: `Ran 5 tests in ... OK`*

### Step 7: Configure Flask
The application generates a random secret key for local use and runs with debug mode disabled by default. For a stable key across restarts, set `FLASK_SECRET_KEY` in your environment. Enable debug mode only for local development by setting `FLASK_DEBUG=true`.

### Step 8: Launch the Application
```powershell
python app.py
```
When running for the first time, the application will automatically:
- Create `database/noise_pollution.db`.
- Populate all 12 zones and 7 standard regulatory noise rules.
- Deploy 30 simulated sensors across Hyderabad.
- Synthesize 500 initial noise readings and evaluate them for violations.

### Step 9: View the Website in your Browser
Open your preferred web browser and navigate to:
```
http://localhost:5000
```

---

## 🖥️ Application Modules & Usage Walkthrough

### 1. Dashboard (`/`)
- Displays overall environmental metrics calculated in real-time from the database.
- Features interactive line charts for the previous 24 hours and noise distribution across land-use zones.
- Includes quick-action triggers to generate telemetry or initiate instant violation audits.

### 2. Interactive Noise Map (`/map`)
- High-performance Leaflet cartography centered on Hyderabad (`17.385° N, 78.487° E`).
- Real-time layer switcher: Toggle individual circle markers or the Gaussian gradient heatmap.
- Filter on the fly by zone category (e.g., Silence, Hospital, Commercial) or decibel classifications.
- Click any sensor pin to inspect its latest telemetry, address, coordinate geometry, and violation status.

### 3. Sensor Management (`/sensors`)
- Live sensor registry with online/offline indicators and last-telemetry readings.
- Search and filter sensors by name, zone assignment, or status.
- Add, edit, or remove sensors with coordinate validation.
- Click the **History** button on any sensor to open an instant telemetry modal with an integrated trendline.

### 4. Zone Management (`/zones`)
- Visual overview of all urban zones with their spatial coverage radius and sensor counts.
- Add new monitoring districts or adjust zone boundaries.

### 5. Violation Monitoring (`/violations`)
- Dedicated audit log of all readings that breached regulatory thresholds.
- Categorized by exceedance levels:
  - `Low` (< 5 dB over threshold)
  - `Medium` (5–15 dB over threshold)
  - `High` (15–25 dB over threshold)
  - `Critical` (> 25 dB over threshold)
- Filter by date range, zone type, and severity. Sensitive zones (hospitals and schools) are highlighted.

### 6. Time-Series Analytics (`/analytics`)
- Aggregated temporal distributions computed using Pandas.
- Hourly profiles highlight rush-hour acoustic signatures.
- Dedicated compliance chart for schools and hospitals directly compares observed noise levels against permissible limits.

### 7. Hotspot Analysis (`/hotspots`)
- Identifies the top 5 noise violation hotspots using weighted multi-variable scoring.
- Zone statistics table shows mean, median, min, max, and standard deviation.
- Generates automated, actionable mitigation recommendations (e.g., soundproofing, traffic calming, no-honking enforcement).

### 8. Reports & CSV Export (`/reports`)
- Comprehensive executive summaries broken down by date range and zone.
- One-click downloads for raw acoustic readings (`noise_readings.csv`) and violation registries (`noise_violations.csv`).
- Print-friendly layout (via browser Print / Save as PDF).

### 9. Settings & Simulation Control (`/settings`)
- View and modify daytime and nighttime decibel thresholds for all zone types.
- Simulation panel allows generating new batches of sensor readings across custom historical windows.
- Includes reset options to clear readings or re-seed the demonstration database.

---

## 🔌 REST API Documentation

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/dashboard/stats` | Aggregated dashboard KPI figures and recent events |
| `GET` | `/api/sensors/` | Retrieve all sensors with latest acoustic readings |
| `POST` | `/api/sensors/` | Register a new sensor (`name`, `latitude`, `longitude`, `zone_id`, `status`) |
| `GET` | `/api/sensors/<id>` | Retrieve sensor details and recent telemetry history |
| `PUT` | `/api/sensors/<id>` | Update sensor attributes |
| `DELETE`| `/api/sensors/<id>` | Remove a sensor and cascade-delete its readings |
| `GET` | `/api/sensors/<id>/readings` | Fetch historical measurements for a specific sensor |
| `GET` | `/api/zones/` | Retrieve all land-use zones with sensor counts |
| `POST` | `/api/zones/` | Create a new spatial zone |
| `PUT` | `/api/zones/<id>` | Update zone metadata or coordinates |
| `DELETE`| `/api/zones/<id>` | Delete a zone and unassign associated sensors |
| `GET` | `/api/violations/` | Query violations with optional filters (`zone_type`, `severity`, dates) |
| `GET` | `/api/violations/<id>` | Retrieve violation detail record |
| `POST` | `/api/violations/detect` | Run the violation detection engine on unanalyzed readings |
| `GET` | `/api/violations/count` | Retrieve violation count with applied filters |
| `GET` | `/api/analytics/hourly` | 24-hour diurnal acoustic trends |
| `GET` | `/api/analytics/daily` | Multi-day average noise levels |
| `GET` | `/api/analytics/zones` | Comparative noise distribution across all zones |
| `GET` | `/api/analytics/peak-hours` | Peak noise hours ranked by average decibels |
| `GET` | `/api/hotspots/` | Top 5 ranked noise violation hotspots |
| `GET` | `/api/hotspots/stats` | Zone-level statistical aggregations (mean, median, std dev) |
| `GET` | `/api/hotspots/recommendations` | Automated mitigation action items |
| `GET` | `/api/reports/summary` | Executive audit summary for reporting |
| `GET` | `/api/reports/export/readings` | Stream raw telemetry measurements as CSV |
| `GET` | `/api/reports/export/violations` | Stream violation records as CSV |
| `GET` | `/api/settings/limits` | Retrieve current permissible decibel thresholds |
| `PUT` | `/api/settings/limits/<id>` | Update daytime/nighttime decibel limits |
| `POST` | `/api/simulate/generate` | Synthesize new batches of simulated readings |
| `POST` | `/api/simulate/reset` | Clear all reading samples and violation events |
| `POST` | `/api/simulate/seed` | Reset and re-seed the demonstration dataset |

---

## 🧮 Statistical Analysis & Hotspot Detection Logic

### 1. Diurnal Permissible Rules
Noise limits vary based on zone classification and time of day:
- **Daytime Window**: 06:00 to 22:00
- **Nighttime Window**: 22:00 to 06:00

```
Exceedance (dB) = Measured Noise (dB) - Applicable Limit (dB)
```
Readings with `Exceedance > 0` generate an immutable violation record.

### 2. Composite Hotspot Scoring
Rather than flagging isolated noise spikes as persistent hotspots, the system uses a weighted multi-factor scoring formula:

$$\text{Score} = (0.30 \times \mu) + (0.40 \times V) + (0.10 \times \text{Max}) + (0.20 \times \sigma)$$

Where:
- $\mu$: Mean acoustic noise level for the zone (dB).
- $V$: Total count of registered violations in the zone.
- $\text{Max}$: Maximum single decibel reading recorded.
- $\sigma$: Standard deviation, capturing acoustic variance and instability.

Zones with high violation counts and elevated average sound levels are prioritized over areas with a single anomalous reading.

---

## ❓ Troubleshooting & Viva FAQs

### Frequently Asked Questions for College Viva

**Q1: Why use SQLite instead of a full client-server database like PostgreSQL?**
> SQLite is zero-configuration, serverless, and self-contained within a single database file, making the application easy to run locally in VS Code without requiring external database server installations. The architecture abstracts queries through `DatabaseManager`, allowing simple migration to PostgreSQL or MySQL for production deployments.

**Q2: How does the system handle time-series data without database bloat?**
> The database uses B-Tree indexes on `sensor_id`, `timestamp`, and `zone_id`. For heavy time-series queries, Pandas handles resampled aggregations (`.resample('h')` / `.groupby()`) in memory, keeping database reads fast and efficient.

**Q3: Are the noise thresholds real regulatory standards?**
> The default thresholds are inspired by the Central Pollution Control Board (CPCB) noise standards for India, adapted for demonstration purposes. Users can configure both daytime and nighttime limits for any zone through the Settings interface.

**Q4: How would physical IoT sensors be integrated?**
> Physical hardware (e.g., ESP32 or Raspberry Pi with an acoustic decibel microphone) can transmit measurements via HTTP `POST` requests to a telemetry endpoint, using the same data schema (`sensor_id`, `timestamp`, `noise_level_db`, coordinates) used by the simulation engine.

---

### Common Setup Issues & Solutions

1. **`python` command is not recognized**
   - Ensure Python is added to your Windows environment `PATH`. Alternatively, use `py app.py` or `python3 app.py`.

2. **PowerShell Script Execution Policy Error**
   - Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` and re-activate the virtual environment.

3. **Port 5000 is already in use**
   - Open `app.py`, scroll to the bottom, and change `port=5000` to `port=5050` or another available port.

4. **Map tiles appear blank or grey**
   - The map requires an active internet connection to fetch OpenStreetMap tiles. Markers and analytics will continue to render once connectivity is restored.

---

*Developed for the Environmental Data Analytics & Smart Cities Engineering Project.*

