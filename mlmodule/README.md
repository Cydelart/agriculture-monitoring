# Iris the Analyst - Simple Student Version 🌱

## What is this?

**Iris** detects unusual sensor readings on your farm plots using Machine Learning (Isolation Forest).

Instead of just checking if temperature is too high, it looks at **combinations** of temperature, humidity, and moisture together. This catches unusual patterns that simple thresholds would miss!

---

## Files (Only 4!)

```
mlmodule/
├── iris_service.py          # MAIN FILE - All the logic (read this!)
├── views.py                 # API endpoints (2 simple functions)
├── urls.py                  # URL routing
└── management/commands/
    └── detect_anomalies.py  # Command line tool
```

That's it! Everything is in **`iris_service.py`** - one file, easy to read.

---

## How to Use

### Option 1: Command Line (Easiest!)

```bash
# Run detection on all plots
pipenv run python manage.py detect_anomalies

# Run on specific plot
pipenv run python manage.py detect_anomalies --plot 1

# Check last 10 minutes of data
pipenv run python manage.py detect_anomalies --minutes 10

# Test without saving to database
pipenv run python manage.py detect_anomalies --no-save
```

### Option 2: In Python Code

```python
from mlmodule.iris_service import run_batch_detection, check_single_reading

# Check recent data (batch)
results = run_batch_detection(
    plot_id=1,      # Which plot? (or None for all)
    minutes=5,      # How far back?
    create_events=True  # Save anomalies to database?
)

# Check a single reading (real-time)
result = check_single_reading(
    plot_id=1,
    temperature=35.5,
    humidity=20.0,
    moisture=15.0,
    create_event=True
)

if result['is_anomaly']:
    print(f"Anomaly detected! Severity: {result['severity']}")
```

### Option 3: REST API

```bash
# Batch detection
POST /api/iris/detect/
{
  "plot_id": 1,
  "minutes": 10,
  "create_events": true
}

# Check single reading
POST /api/iris/check/
{
  "plot_id": 1,
  "temperature": 35.5,
  "humidity": 20.0,
  "moisture": 15.0
}
```

---

## How It Works (Simple Explanation)

### Step 1: Get Sensor Data
```python
# Gets recent sensor readings from database
df = get_sensor_data(plot_id=1, minutes=5)
```

### Step 2: Prepare Vectors
```python
# Groups sensors taken at similar times
# Creates rows like: [temperature, humidity, moisture]
vectors = prepare_vectors(df)
```

### Step 3: Load Model
```python
# Loads the trained Isolation Forest model for this plot
model = load_model(plot_id=1)
```

### Step 4: Detect Anomalies
```python
# The model scores each vector
# Returns -1 for anomaly, 1 for normal
prediction = model.predict([[temperature, humidity, moisture]])
```

### Step 5: Save Results
```python
# If anomaly found, save to AnomalyEvent table
create_anomaly_event(plot_id, timestamp, ...)
```

---

## Testing

Run the simple test:

```bash
pipenv run python mlmodule/test_simple.py
```

This will:
1. ✓ Test normal reading
2. ✓ Test extreme reading (should detect anomaly)
3. ✓ Run batch detection on your data

---

## Understanding the Code

### Main Functions in `iris_service.py`:

| Function | What it does |
|----------|-------------|
| `load_model(plot_id)` | Loads the .joblib model file |
| `get_sensor_data(...)` | Gets readings from database |
| `prepare_vectors(df)` | Combines sensors into rows |
| `detect_anomaly(...)` | Checks if reading is anomalous |
| `create_anomaly_event(...)` | Saves to database |
| **`run_batch_detection(...)`** | **Main batch function** |
| **`check_single_reading(...)`** | **Main real-time function** |

The last two are what you'll actually use!

---

## Configuration

At the top of `iris_service.py`:

```python
# Where models are stored
MODELS_DIR = "agriculture_backend/MLmodels/models"

# Which sensors we need
REQUIRED_SENSORS = ['temperature', 'humidity', 'moisture']

# Default time window (minutes)
DEFAULT_TIME_WINDOW_MINUTES = 5
```

Change these if needed!

---

## Example: Understanding Anomaly Scores

```
Score > 0     = Normal (further from anomalies)
Score = 0     = Borderline
Score < -0.3  = Mild anomaly
Score < -0.5  = Severe anomaly
```

The model assigns severity:
- `low`: Score between -0.3 and -0.1
- `medium`: Score between -0.5 and -0.3
- `high`: Score below -0.5

---

## Viewing Results

### In Django Admin:
1. Go to `/admin/monitoring/anomalyevent/`
2. Look for events with "Unusual sensor combo" in the type
3. These are from Iris!

### In Your Code:
```python
from monitoring.models import AnomalyEvent

# Get recent Iris events
events = AnomalyEvent.objects.filter(
    anomaly_type__icontains='Unusual sensor combo'
).order_by('-timestamp')[:10]

for event in events:
    print(f"Plot {event.plot_id}: {event.severity} at {event.timestamp}")
```

---

## What You Should Understand

1. **Isolation Forest** is a machine learning algorithm that finds unusual patterns
2. Each **plot has its own model** trained on normal data for that plot
3. We need **all three sensors** (temp, humidity, moisture) to make a prediction
4. **Anomaly score** tells us how unusual the reading is
5. We automatically **save anomalies** to the `AnomalyEvent` table

---

## Full Workflow Example

```python
# This is what happens when you run: python manage.py detect_anomalies

# 1. Get data from last 5 minutes
sensor_data = SensorReading.objects.filter(timestamp >= 5 minutes ago)

# 2. Group into vectors (one row = one moment in time)
vectors = group_by_plot_and_second(sensor_data)

# 3. For each vector, check if anomalous
for vector in vectors:
    model = load_model(vector.plot_id)
    is_anomaly = model.predict([temp, humidity, moisture])
    
    # 4. If anomalous, save to database
    if is_anomaly:
        AnomalyEvent.objects.create(...)
```

That's it!

---

## Troubleshooting

**"No model found for plot X"**
- Make sure `isoforest_plot_X.joblib` exists in `agriculture_backend/MLmodels/models/`

**"No sensor data found"**
- Run your simulator to generate recent data
- Or increase `--minutes` to look further back

**"No complete sensor vectors found"**
- Sensors aren't reporting at similar times
- Check that all 3 sensor types are working

---

## Next Steps

1. ✅ Run the test: `pipenv run python mlmodule/test_simple.py`
2. ✅ Try detection: `pipenv run python manage.py detect_anomalies`
3. ✅ Check results in Django admin
4. ✅ Integrate into your dashboard
5. ✅ Schedule to run automatically (cron job)

---

**Questions?** Read the code in `iris_service.py` - it's well commented and straightforward!

**For your report:** Explain that Iris uses Isolation Forest (a tree-based ML algorithm) to detect multivariate anomalies by analyzing sensor combinations rather than individual thresholds.
