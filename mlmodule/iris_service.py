
import os
import pandas as pd
import joblib
from datetime import timedelta
from django.utils import timezone
from monitoring.models import SensorReading, AnomalyEvent, FieldPlot

# --- Config ---
MODELS_DIR = os.path.join(
    os.path.dirname(__file__), 
    "..", "agriculture_backend", "MLmodels", "models"
)
REQUIRED_SENSORS = ['temperature', 'humidity', 'moisture']
DEFAULT_TIME_WINDOW_MINUTES = 5

_model_cache = {}

# --- Helper Functions ---

def load_model(plot_id):
    if plot_id in _model_cache:
        return _model_cache[plot_id]
    
    model_path = os.path.join(MODELS_DIR, f"isoforest_plot_{plot_id}.joblib")
    if not os.path.exists(model_path):
        return None
    
    try:
        model = joblib.load(model_path)
        _model_cache[plot_id] = model
        return model
    except Exception:
        return None


def get_sensor_data(plot_id=None, minutes=DEFAULT_TIME_WINDOW_MINUTES):
    cutoff_time = timezone.now() - timedelta(minutes=minutes)
    query = SensorReading.objects.filter(timestamp__gte=cutoff_time)
    
    if plot_id is not None:
        query = query.filter(plot_id=plot_id)
    
    data = list(query.values('plot_id', 'timestamp', 'sensor_type', 'value'))
    return pd.DataFrame(data) if data else pd.DataFrame()


def prepare_vectors(df):
    if df.empty:
        return pd.DataFrame()
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # Floor to nearest second to group sensors
    df['second'] = df['timestamp'].dt.floor('s')
    
    vectors = df.pivot_table(
        index=['plot_id', 'second'],
        columns='sensor_type',
        values='value',
        aggfunc='mean'
    ).reset_index().rename(columns={'second': 'timestamp'})
    
    return vectors.dropna(subset=REQUIRED_SENSORS)


def detect_anomaly(plot_id, temperature, humidity, moisture):
    model = load_model(plot_id)
    if model is None:
        return {'is_anomaly': False, 'score': 0, 'severity': 'unknown', 'error': 'Model not found'}
    
    X = [[temperature, humidity, moisture]]
    prediction = model.predict(X)[0] # 1 normal, -1 anomaly
    score = model.decision_function(X)[0] # lower = more anomalous
    
    severity = 'low'
    if score < -0.5: severity = 'high'
    elif score < -0.3: severity = 'medium'
    
    return {
        'is_anomaly': prediction == -1,
        'score': float(score),
        'severity': severity
    }


def create_anomaly_event(plot_id, timestamp, temperature, humidity, moisture, score, severity):
    try:
        plot = FieldPlot.objects.get(id=plot_id)
        description = f"Unusual sensor combo: T={temperature:.1f}, H={humidity:.1f}, M={moisture:.1f}"
        
        return AnomalyEvent.objects.create(
            plot=plot,
            timestamp=timestamp,
            anomaly_type=description[:100],
            severity=severity,
            model_confidence=abs(score)
        )
    except Exception:
        return None

# --- Main Interfaces ---

def run_batch_detection(plot_id=None, minutes=DEFAULT_TIME_WINDOW_MINUTES, create_events=True):
    df = get_sensor_data(plot_id, minutes)
    if df.empty:
        return {'success': False, 'message': 'No data found'}
    
    vectors = prepare_vectors(df)
    if vectors.empty:
        return {'success': False, 'message': 'No complete vectors'}
    
    results_by_plot = {}
    total_analyzed = 0
    anomalies_found = 0
    events_created = 0
    
    for pid in vectors['plot_id'].unique():
        plot_vectors = vectors[vectors['plot_id'] == pid]
        plot_anomalies = 0
        
        for _, row in plot_vectors.iterrows():
            result = detect_anomaly(pid, row['temperature'], row['humidity'], row['moisture'])
            total_analyzed += 1
            
            if result['is_anomaly']:
                anomalies_found += 1
                plot_anomalies += 1
                
                if create_events:
                    create_anomaly_event(
                        pid, row['timestamp'], row['temperature'], row['humidity'], 
                        row['moisture'], result['score'], result['severity']
                    )
                    events_created += 1
        
        results_by_plot[int(pid)] = {'analyzed': len(plot_vectors), 'anomalies': plot_anomalies}
            
    return {
        'success': True,
        'total_analyzed': total_analyzed,
        'anomalies_found': anomalies_found,
        'events_created': events_created,
        'by_plot': results_by_plot
    }


def check_single_reading(plot_id, temperature, humidity, moisture, create_event=True):
    result = detect_anomaly(plot_id, temperature, humidity, moisture)
    
    if result['is_anomaly'] and create_event:
        event = create_anomaly_event(
            plot_id, timezone.now(), temperature, humidity, moisture, 
            result['score'], result['severity']
        )
        result['event_id'] = event.id if event else None
        
    return result
