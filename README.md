# Intelligent Classroom Energy Monitoring System
**Final Year B.Tech Project — MIT School of Computing, MITADT University**

---

## Phase 18 — Final End-to-End Architecture

```
REAL CLASSROOM
│
├── Energy Sensors (CT clamps / PZEM-004T on each circuit)
│     light_circuit → light_power_w
│     fan_circuit   → fan_power_w
│     projector     → projector_power_w
│
├── Context Sensors
│     DHT22         → temperature, humidity
│     PIR / manual  → occupancy
│     BH1750        → light_intensity
│
↓
ESP32 Microcontroller  [TEAMMATES' RESPONSIBILITY]
│   Reads sensors every 10 minutes
│   Computes total_power_w and energy_kwh
│   Publishes via Wi-Fi → MQTT broker OR HTTP POST
│
↓
FastAPI Backend  [MY RESPONSIBILITY]
│   POST /api/sensor-data   → ingests & validates payload
│   GET  /api/current       → latest reading
│   GET  /api/history       → aggregated history
│   GET  /api/prediction    → on-demand prediction
│   GET  /api/anomalies     → anomaly log
│
↓
SQLite Database (→ PostgreSQL in production)  [MY RESPONSIBILITY]
│   sensor_readings   table
│   predictions       table
│   anomalies         table
│
↓
ML Pipeline  [MY RESPONSIBILITY]
│   preprocessing.py  → feature engineering
│   predict.py        → XGBoost inference (v1.0)
│   anomaly.py        → residual + appliance attribution
│
├── Energy Forecast
│     XGBoost → predicted_next_interval_wh
│     LSTM    → available, better R² (0.58 vs 0.35)
│
└── Anomaly Detection
      Residual method (3σ threshold from validation set)
      Isolation Forest (secondary, 2% contamination)
      Appliance attribution → pending real ESP32 data
│
↓
Dashboard / Classroom Display  [SHARED / INTEGRATION]
    Current panel    → live W readings per appliance
    Historical panel → hourly/daily kWh charts
    AI panel         → predictions + anomaly alerts
```

---

## Responsibility Map

| Component | Owner |
|---|---|
| CT clamp / PZEM sensors, wiring | Teammates |
| ESP32 firmware, MQTT/HTTP publish | Teammates |
| FastAPI backend (`/backend/`) | **You** |
| Database schema + queries | **You** |
| ML pipeline (`/ml/`) | **You** |
| Anomaly detection logic | **You** |
| Dashboard frontend | Shared / TBD |
| WiFi network / broker setup | Shared |

---

## Project Structure

```
project/
├── backend/
│   ├── main.py              ← FastAPI app entry point
│   ├── api/
│   │   ├── sensor.py        ← POST /api/sensor-data
│   │   ├── energy.py        ← GET  /api/current, /api/history
│   │   ├── prediction.py    ← GET  /api/prediction
│   │   └── anomaly.py       ← GET  /api/anomalies
│   ├── schemas/
│   │   └── schemas.py       ← Pydantic request/response models
│   └── database/
│       └── db.py            ← SQLite connection + init_db()
│
├── ml/
│   ├── preprocessing.py     ← Feature engineering (shared)
│   ├── predict.py           ← Inference only (loads saved model)
│   ├── anomaly.py           ← Appliance-level attribution
│   └── models/
│       ├── xgboost_tuned.json
│       ├── anomaly_thresholds.npy
│       └── lstm_model.keras
│
├── data/
│   ├── schema.sql           ← Database schema
│   └── classroom_energy.db  ← SQLite DB (auto-created)
│
├── notebooks/               ← EDA + training notebooks
└── README.md
```

---

## How to Run

```bash
# 1. Install dependencies
pip install fastapi uvicorn xgboost scikit-learn pandas numpy pydantic

# 2. Start the server
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 3. API docs (auto-generated)
# Open: http://localhost:8000/docs

# 4. Test with simulated ESP32 data
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

---

## Model Performance (UCI Public Dataset — Not Classroom Data)

| Model | MAE (Wh) | RMSE (Wh) | R² | Train Time |
|---|---|---|---|---|
| Naive Baseline | 34.65 | 88.88 | 0.055 | <0.01s |
| Linear Regression | 33.30 | 74.10 | 0.343 | 0.02s |
| Random Forest | 45.65 | 81.08 | 0.214 | 19.1s |
| XGBoost (tuned) | 34.14 | 73.67 | 0.351 | 0.2s |
| **LSTM** | **23.73** | **59.39** | **0.575** | 123.7s |

**Selected model for inference: XGBoost (tuned)**
- Best balance of accuracy and inference speed for real-time API
- LSTM available as an upgrade when latency permits

---

## Limitations

1. **Dataset mismatch**: Trained on Belgian household data (2016). Classroom patterns will differ significantly — occupancy-driven peaks, class schedules, etc.
2. **No occupancy feature**: UCI dataset has no occupancy data; this is the single most important missing feature for a classroom system.
3. **Appliance attribution**: Cannot validate fan/projector anomaly logic without real per-circuit ESP32 data.
4. **Cold start**: Lag features need ≥ 1008 readings (7 days) of history before reaching full accuracy. Rolling means are filled with available history in the interim.
5. **Model drift**: As seasons change, the model should be retrained periodically on accumulated ESP32 data.

---

## Future Integration with ESP32

When the hardware team delivers sensor data:

1. Run `POST /api/sensor-data` for every 10-minute reading.
2. After 7 days of real data, retrain the XGBoost model using the same `train.py` pipeline.
3. Replace `ml/models/xgboost_tuned.json` with the new model (`v2.0`).
4. Anomaly thresholds will automatically recalibrate on the new validation residuals.
5. Add `occupancy` as a feature — it will likely be the single largest improvement.

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/sensor-data` | POST | Ingest ESP32 reading, return prediction |
| `/api/current` | GET | Latest sensor reading |
| `/api/history` | GET | Aggregated history (raw/hourly/daily) |
| `/api/prediction` | GET | On-demand prediction from latest data |
| `/api/anomalies` | GET | List of detected anomaly events |

Full interactive docs at `http://localhost:8000/docs` (Swagger UI).
