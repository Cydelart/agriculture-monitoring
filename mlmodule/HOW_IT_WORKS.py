"""
Visual Guide: How Iris Works (Simplified)

This shows the flow from sensor data to anomaly detection.
"""

# ============================================================================
# STEP-BY-STEP VISUAL FLOW
# ============================================================================

"""
STEP 1: Sensor Data in Database
================================

SensorReading Table:
┌────────┬─────────────────────┬──────────────┬───────┐
│ plot_id│ timestamp           │ sensor_type  │ value │
├────────┼─────────────────────┼──────────────┼───────┤
│ 1      │ 2025-12-15 10:00:00 │ temperature  │ 22.5  │
│ 1      │ 2025-12-15 10:00:00 │ humidity     │ 65.0  │
│ 1      │ 2025-12-15 10:00:00 │ moisture     │ 45.0  │
│ 1      │ 2025-12-15 10:00:01 │ temperature  │ 22.4  │
│ 1      │ 2025-12-15 10:00:01 │ humidity     │ 64.8  │
│ 1      │ 2025-12-15 10:00:01 │ moisture     │ 44.9  │
└────────┴─────────────────────┴──────────────┴───────┘


STEP 2: prepare_vectors() Groups Them
=====================================

From this (3 rows per second):
  temperature=22.5, humidity=65.0, moisture=45.0

To this (1 row per second):
┌────────┬─────────────────────┬──────────────┬──────────┬──────────┐
│ plot_id│ timestamp           │ temperature  │ humidity │ moisture │
├────────┼─────────────────────┼──────────────┼──────────┼──────────┤
│ 1      │ 2025-12-15 10:00:00 │ 22.5         │ 65.0     │ 45.0     │
│ 1      │ 2025-12-15 10:00:01 │ 22.4         │ 64.8     │ 44.9     │
└────────┴─────────────────────┴──────────────┴──────────┴──────────┘


STEP 3: load_model() Gets the ML Model
=======================================

Loads this file:
📁 agriculture_backend/MLmodels/models/isoforest_plot_1.joblib

The model is a tree-based algorithm that learned what "normal" looks like.


STEP 4: detect_anomaly() Makes Prediction
==========================================

Input to model:
  [[22.5, 65.0, 45.0]]  ← One vector

Model outputs:
  prediction = 1      ← (1 = normal, -1 = anomaly)
  score = 0.25        ← (negative = anomaly, positive = normal)

We convert to:
  is_anomaly = False
  severity = "low"


STEP 5: If Anomaly, Save to Database
=====================================

AnomalyEvent Table:
┌────────┬─────────────────────┬─────────────────────┬──────────┬────────────┐
│ plot_id│ timestamp           │ anomaly_type        │ severity │ confidence │
├────────┼─────────────────────┼─────────────────────┼──────────┼────────────┤
│ 1      │ 2025-12-15 10:05:30 │ Unusual sensor combo│ high     │ 0.78       │
└────────┴─────────────────────┴─────────────────────┴──────────┴────────────┘
"""

# ============================================================================
# CODE FLOW: Function Calls
# ============================================================================

"""
When you run: python manage.py detect_anomalies

Here's what happens:

1. Command.handle() in detect_anomalies.py
   ↓
2. run_batch_detection() in iris_service.py
   ↓
3. get_sensor_data()          ← Gets data from database
   ↓
4. prepare_vectors()           ← Groups into [T, H, M] rows
   ↓
5. load_model()                ← Loads .joblib file
   ↓
6. detect_anomaly()            ← For each vector
   ↓
7. create_anomaly_event()      ← If anomaly detected
   ↓
8. Print summary

All in ONE file (iris_service.py)!
"""

# ============================================================================
# EXAMPLE: Detecting One Anomaly
# ============================================================================

"""
Let's say we have this reading:
  Temperature = 50°C   (very hot!)
  Humidity = 10%       (very dry!)
  Moisture = 5%        (very dry soil!)

Step 1: Load model for plot 1
  model = joblib.load('isoforest_plot_1.joblib')

Step 2: Prepare input
  X = [[50.0, 10.0, 5.0]]

Step 3: Get prediction
  prediction = model.predict(X)      → [-1]  (anomaly!)
  score = model.decision_function(X) → [-0.85] (very anomalous!)

Step 4: Determine severity
  score = -0.85 < -0.5, so severity = "high"

Step 5: Create event
  AnomalyEvent.objects.create(
      plot_id=1,
      severity="high",
      anomaly_type="Unusual sensor combo: T=50.0°C, H=10.0%, M=5.0%",
      model_confidence=0.85
  )

Done! The anomaly is now in the database.
"""

# ============================================================================
# FILE STRUCTURE VISUAL
# ============================================================================

"""
mlmodule/
│
├── 🧠 iris_service.py          ← THE BRAIN (all logic here)
│   ├── load_model()            ← Load .joblib file
│   ├── get_sensor_data()       ← Query database
│   ├── prepare_vectors()       ← Group sensors
│   ├── detect_anomaly()        ← ML prediction
│   ├── create_anomaly_event()  ← Save to DB
│   ├── run_batch_detection()   ← Main batch function
│   └── check_single_reading()  ← Main realtime function
│
├── 📡 views.py                  ← API ENDPOINTS
│   ├── batch_detect()          ← POST /api/iris/detect/
│   └── check_reading()         ← POST /api/iris/check/
│
├── 🔗 urls.py                   ← URL ROUTING (connects URLs to views)
│
└── 💻 management/commands/
    └── detect_anomalies.py     ← COMMAND LINE TOOL

That's it! Clean and simple.
"""

# ============================================================================
# WHAT YOU NEED TO KNOW
# ============================================================================

"""
For Your Report/Understanding:

1. ISOLATION FOREST
   - Machine learning algorithm
   - Finds data points that are "isolated" (different from others)
   - No training on anomalies needed, only normal data
   - Works by building random trees

2. MULTIVARIATE DETECTION
   - "Multivariate" = multiple variables
   - We look at T, H, M together
   - Can catch patterns like "high temp + low humidity"
   - Better than checking each sensor separately

3. PLOT-SPECIFIC MODELS
   - Each plot has different "normal" conditions
   - Plot 1 might be drier than Plot 2 normally
   - So we train one model per plot
   - More accurate than one global model

4. THE WORKFLOW
   Database → Group Sensors → ML Model → Anomaly Event
   
5. USAGE
   - Command: python manage.py detect_anomalies
   - Python: from mlmodule.iris_service import run_batch_detection
   - API: POST /api/iris/detect/
"""

if __name__ == "__main__":
    print(__doc__)
