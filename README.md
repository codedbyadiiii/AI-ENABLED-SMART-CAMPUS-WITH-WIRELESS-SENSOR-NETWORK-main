# AI-Enabled Smart Campus

An intelligent classroom energy monitoring system that combines wireless sensor data, a FastAPI backend, SQLite persistence, machine-learning predictions, and anomaly detection.

## Overview

The system is designed to collect classroom telemetry from an ESP32-based sensor network and provide actionable energy insights through a REST API.

### Key capabilities

- Ingests temperature, humidity, occupancy, lighting, and appliance energy readings
- Validates and stores sensor readings in SQLite
- Provides current and historical energy data
- Predicts energy usage for the next interval using XGBoost
- Detects unusual energy consumption using residual analysis and appliance attribution
- Exposes interactive API documentation through FastAPI and Swagger UI

## Architecture

```text
Energy and context sensors
        |
        v
ESP32 sensor node
        |
        | HTTP or MQTT integration
        v
FastAPI REST API
        |
        +--> SQLite database
        |
        +--> ML inference and anomaly detection
        |
        v
Dashboard or classroom display
```

The sensor layer can publish readings from CT clamps or PZEM-004T energy meters, DHT22 temperature and humidity sensors, PIR occupancy sensors, and BH1750 light sensors.

## Technology Stack

- **Backend:** Python, FastAPI, Pydantic, Uvicorn
- **Database:** SQLite
- **Machine learning:** XGBoost, scikit-learn, NumPy, pandas
- **Hardware integration:** ESP32 with HTTP or MQTT publishing
- **API documentation:** OpenAPI and Swagger UI

## Repository Structure

```text
.
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── sensor.py           # Sensor data ingestion
│   │   ├── energy.py           # Current and historical energy data
│   │   ├── prediction.py       # Energy prediction endpoint
│   │   └── anomaly.py          # Anomaly endpoint
│   ├── database/
│   │   └── db.py               # SQLite connection and initialization
│   └── schemas/
│       └── schemas.py          # Request and response models
├── data/
│   └── schema.sql              # Database schema
├── ml/
│   ├── preprocessing.py        # Feature engineering
│   ├── predict.py              # Model inference
│   ├── anomaly.py              # Anomaly detection and attribution
│   └── models/                 # Trained model artifacts
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.9 or later
- `pip`

### Installation

1. Clone the repository and enter the project directory:

   ```bash
   git clone https://github.com/codedbyadiiii/AI-ENABLED-SMART-CAMPUS-WITH-WIRELESS-SENSOR-NETWORK-main.git
   cd AI-ENABLED-SMART-CAMPUS-WITH-WIRELESS-SENSOR-NETWORK-main
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   On Windows, use:

   ```powershell
   .venv\Scripts\activate
   ```

3. Install the dependencies:

   ```bash
   pip install fastapi uvicorn xgboost scikit-learn pandas numpy pydantic
   ```

### Run the API

From the repository root:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Open the following URLs after the server starts:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## API Endpoints

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/sensor-data` | `POST` | Ingest a sensor reading and return a prediction |
| `/api/current` | `GET` | Return the latest sensor reading |
| `/api/history` | `GET` | Return raw, hourly, or daily historical data |
| `/api/prediction` | `GET` | Generate a prediction from the latest available data |
| `/api/anomalies` | `GET` | List detected energy anomalies |

### Example sensor request

```bash
curl -X POST http://localhost:8000/api/sensor-data \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2024-01-15T10:30:00",
    "light_power_w": 320,
    "fan_power_w": 450,
    "projector_power_w": 280,
    "total_power_w": 1050,
    "energy_kwh": 0.175,
    "occupancy": 25,
    "temperature": 27.3,
    "light_intensity": 540
  }'
```

## Machine Learning

The current inference pipeline uses a tuned XGBoost model selected for its balance of prediction accuracy and API response time. The anomaly detector combines residual thresholds with appliance-level attribution.

The included model evaluation results are based on a public UCI household energy dataset:

| Model | MAE (Wh) | RMSE (Wh) | R2 |
| --- | ---: | ---: | ---: |
| Naive baseline | 34.65 | 88.88 | 0.055 |
| Linear regression | 33.30 | 74.10 | 0.343 |
| Random forest | 45.65 | 81.08 | 0.214 |
| XGBoost | 34.14 | 73.67 | 0.351 |
| LSTM | 23.73 | 59.39 | 0.575 |

The LSTM result is included for comparison; XGBoost is the selected production inference model in this repository.

## Hardware Integration

An ESP32 node can collect readings at a configurable interval and publish them to the backend over Wi-Fi. A typical deployment may include:

- CT clamps or PZEM-004T meters for appliance-level power measurement
- DHT22 for temperature and humidity
- PIR or manual input for occupancy
- BH1750 for ambient light intensity

MQTT or a direct HTTP integration can be added at the sensor gateway layer without changing the core ML pipeline.

## Limitations and Future Work

- The model was trained on Belgian household energy data rather than classroom data.
- Occupancy is collected by the API but is not represented in the current trained model.
- Appliance attribution requires real per-circuit sensor data for validation.
- The model should be retrained periodically using accumulated classroom readings.
- PostgreSQL, authentication, monitoring, and a production dashboard are recommended for deployment at scale.

## Project Context

This project was developed as a final-year B.Tech project at MIT School of Computing, MITADT University. The backend, database, machine-learning pipeline, and anomaly detection components are organized to support future ESP32 and dashboard integration.

## License

No license has been specified yet. Add a license before accepting external contributions or redistributing the project.
