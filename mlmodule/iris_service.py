import os
import re
import pandas as pd
import joblib
from datetime import timedelta
from django.utils import timezone
from monitoring.models import SensorReading, AnomalyEvent, FieldPlot


MODELS_DIR = os.path.join(
    os.path.dirname(__file__),
    ".", "agriculture_backend", "MLmodels", "models"
)

REQUIRED_SENSORS = ["temperature", "humidity", "moisture"]
DEFAULT_TIME_WINDOW_MINUTES = 5

_model_cache = {}


def load_model(plot_id: int):
    
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

    data = list(query.values("plot_id", "timestamp", "sensor_type", "value"))
    return pd.DataFrame(data) if data else pd.DataFrame()


def prepare_vectors(df: pd.DataFrame):
    #Prepare sensor vectors from raw readings taatina dataframe with plot_id, timestamp, sensor_type, value
    if df.empty:
        return pd.DataFrame()

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["second"] = df["timestamp"].dt.floor("s")

    vectors = (
        df.pivot_table(
            index=["plot_id", "second"],
            columns="sensor_type",
            values="value",
            aggfunc="mean",
        )
        .reset_index()
        .rename(columns={"second": "timestamp"})
    )

    return vectors.dropna(subset=REQUIRED_SENSORS)


def detect_anomaly(plot_id, temperature, humidity, moisture):
    #Detect anomaly for one vector.
    #trajeelna score w isanomaly w severity
    
    model = load_model(plot_id)
    if model is None:
        return {
            "is_anomaly": False,
            "score": 0.0,
            "severity": "unknown",
            "error": "Model not found",
        }

    X = [[temperature, humidity, moisture]]
    prediction = model.predict(X)[0]  # 1 normal, -1 anomaly
    score = model.decision_function(X)[0]  # lower = more anomalous

    severity = "low"
    if score < -0.5:
        severity = "high"
    elif score < -0.3:
        severity = "medium"

    return {
        "is_anomaly": prediction == -1,
        "score": float(score),
        "severity": severity,
    }


def anomaly_event_exists(plot_id, timestamp):
    return AnomalyEvent.objects.filter(plot_id=plot_id, timestamp=timestamp).exists()


def create_anomaly_event(plot_id, timestamp, temperature, humidity, moisture, score, severity, no_duplicates=True):
   

    try:
        if no_duplicates and anomaly_event_exists(plot_id, timestamp):
            existing = (
                AnomalyEvent.objects.filter(plot_id=plot_id, timestamp=timestamp)
                .only("id")
                .first()
            )
            return existing, False

        plot = FieldPlot.objects.get(id=plot_id)
        description = f"Unusual sensor combo: T={temperature:.1f}, H={humidity:.1f}, M={moisture:.1f}"

        event = AnomalyEvent.objects.create(
            plot=plot,
            timestamp=timestamp,
            anomaly_type=description[:100],
            severity=severity,
            model_confidence=abs(score),
        )
        return event, True

    except Exception:
        return None, False


# -----------------------------------------------------------------------------
# Main function nrunniw batch detection for 3 plots 
# -----------------------------------------------------------------------------
def run_batch_detection(plot_id=None, minutes=DEFAULT_TIME_WINDOW_MINUTES, create_events=True, no_duplicates=True):
   
    df = get_sensor_data(plot_id, minutes)
    if df.empty:
        return {"success": False, "message": "No data found"}

    vectors = prepare_vectors(df)
    if vectors.empty:
        return {"success": False, "message": "No complete vectors"}

    results_by_plot = {}
    total_analyzed = 0
    anomalies_found = 0
    events_created = 0
    duplicates_skipped = 0

    # we loop over vectors per plot
    for pid in vectors["plot_id"].unique():
        pid = int(pid)
        plot_vectors = vectors[vectors["plot_id"] == pid]

        plot_analyzed = 0
        plot_anomalies = 0
        plot_events_created = 0
        plot_duplicates = 0

        for _, row in plot_vectors.iterrows():
            plot_analyzed += 1
            total_analyzed += 1

            res = detect_anomaly(pid, row["temperature"], row["humidity"], row["moisture"])

            if res.get("is_anomaly"):
                plot_anomalies += 1
                anomalies_found += 1

                if create_events:
                    event, created = create_anomaly_event(
                        pid,
                        row["timestamp"],
                        row["temperature"],
                        row["humidity"],
                        row["moisture"],
                        res["score"],
                        res["severity"],
                        no_duplicates=no_duplicates,
                    )

                    if created:
                        plot_events_created += 1
                        events_created += 1
                    else:
                        # only count as duplicate if it existed (not if None due to error)
                        if event is not None:
                            plot_duplicates += 1
                            duplicates_skipped += 1

        plot_rate = (plot_anomalies / plot_analyzed) if plot_analyzed else 0.0

        results_by_plot[pid] = {
            "analyzed": plot_analyzed,
            "anomalies": plot_anomalies,
            "anomaly_rate": plot_rate,
            "events_created": plot_events_created,
            "duplicates_skipped": plot_duplicates,
        }

    anomaly_rate = (anomalies_found / total_analyzed) if total_analyzed else 0.0

    return {
        "success": True,
        "minutes": minutes,
        "total_analyzed": total_analyzed,
        "anomalies_found": anomalies_found,
        "anomaly_rate": anomaly_rate,
        "events_created": events_created,
        "by_plot": results_by_plot,
    }


def check_single_reading(plot_id, temperature, humidity, moisture, create_event=True):
    #ma nesthakouhouch for now , it does detection for one reading and create event if needed
    result = detect_anomaly(plot_id, temperature, humidity, moisture)

    if result["is_anomaly"] and create_event:
        event, _created = create_anomaly_event(
            plot_id,
            timezone.now(),
            temperature,
            humidity,
            moisture,
            result["score"],
            result["severity"],
            no_duplicates=False,  # single reading is "now", duplication usually not an issue
        )
        result["event_id"] = event.id if event else None

    return result
