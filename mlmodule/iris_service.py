"""
Iris the Analyst - Simplified Anomaly Detection Service

This single file contains everything you need for anomaly detection:
- Loading models
- Processing sensor data
- Detecting anomalies
- Creating events

Simple and easy to understand!
"""
import os
import pandas as pd
import joblib
from datetime import timedelta
from django.utils import timezone
from monitoring.models import SensorReading, AnomalyEvent, FieldPlot


# ============================================================================
# CONFIGURATION (Easy to modify)
# ============================================================================

# Where are the models stored?
MODELS_DIR = os.path.join(
    os.path.dirname(__file__), 
    "..", 
    "agriculture_backend", 
    "MLmodels", 
    "models"
)

# Which sensors do we need?
REQUIRED_SENSORS = ['temperature', 'humidity', 'moisture']

# How far back to look for data (in minutes)
DEFAULT_TIME_WINDOW_MINUTES = 5

# Cache for models (avoid loading from disk every time)
_model_cache = {}


# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def load_model(plot_id):
    """
    Load the Isolation Forest model for a specific plot.
    
    Args:
        plot_id: The plot ID (1, 2, 3, etc.)
    
    Returns:
        The loaded model, or None if not found
    """
    # Check if already loaded
    if plot_id in _model_cache:
        return _model_cache[plot_id]
    
    # Load from disk
    model_path = os.path.join(MODELS_DIR, f"isoforest_plot_{plot_id}.joblib")
    
    if not os.path.exists(model_path):
        print(f"Warning: No model found for plot {plot_id}")
        return None
    
    try:
        model = joblib.load(model_path)
        _model_cache[plot_id] = model  # Cache it
        print(f"Loaded model for plot {plot_id}")
        return model
    except Exception as e:
        print(f"Error loading model for plot {plot_id}: {e}")
        return None


def get_sensor_data(plot_id=None, minutes=DEFAULT_TIME_WINDOW_MINUTES):
    """
    Get recent sensor readings from the database.
    
    Args:
        plot_id: Specific plot to get data for (None = all plots)
        minutes: How many minutes back to look
    
    Returns:
        DataFrame with sensor readings
    """
    # Calculate time cutoff
    cutoff_time = timezone.now() - timedelta(minutes=minutes)
    
    # Query database
    query = SensorReading.objects.filter(timestamp__gte=cutoff_time)
    
    if plot_id is not None:
        query = query.filter(plot_id=plot_id)
    
    # Convert to DataFrame
    data = list(query.values('plot_id', 'timestamp', 'sensor_type', 'value'))
    
    if not data:
        print(f"No sensor data found in the last {minutes} minutes")
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    print(f"Found {len(df)} sensor readings")
    return df


def prepare_vectors(df):
    """
    Convert sensor readings into feature vectors for the model.
    
    We need one row with all three sensors (temperature, humidity, moisture).
    Group readings by plot and second to handle slight timing differences.
    
    Args:
        df: DataFrame with sensor readings
    
    Returns:
        DataFrame where each row has: plot_id, timestamp, temperature, humidity, moisture
    """
    if df.empty:
        return pd.DataFrame()
    
    # Make sure timestamp is datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Round timestamp to nearest second (groups sensors taken at similar times)
    df['second'] = df['timestamp'].dt.floor('s')
    
    # Pivot: one row per plot + second, columns for each sensor type
    vectors = df.pivot_table(
        index=['plot_id', 'second'],
        columns='sensor_type',
        values='value',
        aggfunc='mean'  # Average if multiple readings
    ).reset_index()
    
    # Rename 'second' back to 'timestamp'
    vectors = vectors.rename(columns={'second': 'timestamp'})
    
    # Keep only complete rows (all three sensors present)
    complete_vectors = vectors.dropna(subset=REQUIRED_SENSORS)
    
    print(f"Created {len(complete_vectors)} complete sensor vectors")
    return complete_vectors


def detect_anomaly(plot_id, temperature, humidity, moisture):
    """
    Check if a sensor reading combination is anomalous.
    
    Args:
        plot_id: Which plot
        temperature: Temperature value
        humidity: Humidity value
        moisture: Moisture value
    
    Returns:
        Dictionary with:
            - is_anomaly: True/False
            - score: Anomaly score (lower = more anomalous)
            - severity: 'low', 'medium', or 'high'
    """
    # Load the model for this plot
    model = load_model(plot_id)
    
    if model is None:
        return {
            'is_anomaly': False,
            'score': 0,
            'severity': 'unknown',
            'error': 'Model not found'
        }
    
    # Prepare the input (model expects a 2D array)
    X = [[temperature, humidity, moisture]]
    
    # Get prediction
    # predict() returns 1 for normal, -1 for anomaly
    prediction = model.predict(X)[0]
    
    # Get anomaly score (lower = more anomalous)
    score = model.decision_function(X)[0]
    
    # Determine severity based on score
    if score < -0.5:
        severity = 'high'
    elif score < -0.3:
        severity = 'medium'
    else:
        severity = 'low'
    
    return {
        'is_anomaly': prediction == -1,
        'score': float(score),
        'severity': severity
    }


def create_anomaly_event(plot_id, timestamp, temperature, humidity, moisture, score, severity):
    """
    Create an AnomalyEvent record in the database.
    
    Args:
        plot_id: Which plot
        timestamp: When the anomaly occurred
        temperature, humidity, moisture: Sensor values
        score: Anomaly score
        severity: 'low', 'medium', or 'high'
    
    Returns:
        The created AnomalyEvent, or None if failed
    """
    try:
        plot = FieldPlot.objects.get(id=plot_id)
        
        # Create description
        description = f"Unusual sensor combo: T={temperature:.1f}°C, H={humidity:.1f}%, M={moisture:.1f}%"
        
        event = AnomalyEvent.objects.create(
            plot=plot,
            timestamp=timestamp,
            anomaly_type=description[:50],  # Truncate to fit
            severity=severity,
            model_confidence=abs(score)
        )
        
        print(f"Created anomaly event: {event.id}")
        return event
        
    except Exception as e:
        print(f"Error creating event: {e}")
        return None


# ============================================================================
# MAIN DETECTION FUNCTIONS (These are what you'll use!)
# ============================================================================

def run_batch_detection(plot_id=None, minutes=DEFAULT_TIME_WINDOW_MINUTES, create_events=True):
    """
    Run anomaly detection on recent sensor data.
    
    This is the main function to use for batch processing.
    
    Args:
        plot_id: Specific plot to check (None = all plots)
        minutes: How many minutes of data to analyze
        create_events: Whether to save anomalies to database
    
    Returns:
        Dictionary with results summary
    """
    print(f"\n{'='*60}")
    print(f"Running Iris Anomaly Detection")
    print(f"Plot: {plot_id or 'all'}, Time window: {minutes} minutes")
    print(f"{'='*60}\n")
    
    # Step 1: Get sensor data
    df = get_sensor_data(plot_id, minutes)
    
    if df.empty:
        return {
            'success': False,
            'message': 'No data found',
            'total_analyzed': 0,
            'anomalies_found': 0
        }
    
    # Step 2: Prepare feature vectors
    vectors = prepare_vectors(df)
    
    if vectors.empty:
        return {
            'success': False,
            'message': 'No complete sensor vectors found',
            'total_analyzed': 0,
            'anomalies_found': 0
        }
    
    # Step 3: Detect anomalies
    total_analyzed = 0
    anomalies_found = 0
    events_created = 0
    results_by_plot = {}
    
    for pid in vectors['plot_id'].unique():
        plot_vectors = vectors[vectors['plot_id'] == pid]
        plot_anomalies = 0
        
        print(f"\nAnalyzing Plot {pid}: {len(plot_vectors)} vectors")
        
        for _, row in plot_vectors.iterrows():
            result = detect_anomaly(
                pid,
                row['temperature'],
                row['humidity'],
                row['moisture']
            )
            
            total_analyzed += 1
            
            if result['is_anomaly']:
                anomalies_found += 1
                plot_anomalies += 1
                
                print(f"  ⚠ Anomaly detected! Score: {result['score']:.3f}, Severity: {result['severity']}")
                print(f"     T={row['temperature']:.1f}°C, H={row['humidity']:.1f}%, M={row['moisture']:.1f}%")
                
                # Create event if requested
                if create_events:
                    event = create_anomaly_event(
                        pid,
                        row['timestamp'],
                        row['temperature'],
                        row['humidity'],
                        row['moisture'],
                        result['score'],
                        result['severity']
                    )
                    if event:
                        events_created += 1
        
        results_by_plot[int(pid)] = {
            'analyzed': len(plot_vectors),
            'anomalies': plot_anomalies
        }
    
    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"Total vectors analyzed: {total_analyzed}")
    print(f"Anomalies detected: {anomalies_found}")
    print(f"Events created: {events_created}")
    print(f"{'='*60}\n")
    
    return {
        'success': True,
        'total_analyzed': total_analyzed,
        'anomalies_found': anomalies_found,
        'events_created': events_created,
        'by_plot': results_by_plot
    }


def check_single_reading(plot_id, temperature, humidity, moisture, create_event=True):
    """
    Check a single sensor reading for anomalies.
    
    Use this for real-time detection as new readings come in.
    
    Args:
        plot_id: Which plot
        temperature, humidity, moisture: Sensor values
        create_event: Whether to save anomaly to database
    
    Returns:
        Dictionary with detection results
    """
    print(f"Checking single reading for plot {plot_id}")
    print(f"  T={temperature}°C, H={humidity}%, M={moisture}%")
    
    # Detect anomaly
    result = detect_anomaly(plot_id, temperature, humidity, moisture)
    
    if result['is_anomaly']:
        print(f"  ⚠ ANOMALY! Score: {result['score']:.3f}, Severity: {result['severity']}")
        
        # Create event if requested
        if create_event:
            event = create_anomaly_event(
                plot_id,
                timezone.now(),
                temperature,
                humidity,
                moisture,
                result['score'],
                result['severity']
            )
            result['event_id'] = event.id if event else None
    else:
        print(f"  ✓ Normal. Score: {result['score']:.3f}")
    
    return result
