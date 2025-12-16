import os
import sys

import django
import joblib
import pandas as pd





# --- Django setup (standalone script) ---
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "agriculture_backend.settings"
)

django.setup()

from monitoring.models import SensorReading


# --- Config ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

FEATURES = ["temperature", "humidity", "moisture"]
SOURCE_VALUE = "simulator_scenarios"
LIMIT = 1500


def fetch_vectors(limit=LIMIT, source=SOURCE_VALUE):
    qs = (
        SensorReading.objects
        .filter(source=source)
        .order_by("-timestamp")[:limit]
        .values("plot_id", "timestamp", "sensor_type", "value")
    )

    # ORM → DataFrame
    # create dataframe with pandas bch najmou naamlou preprocessing to apply ml
    df = pd.DataFrame(list(qs))

    if df.empty:
        return pd.DataFrame()

    # FIX: Timestamp bucketing (critical) understandable by pandas
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["bucket"] = df["timestamp"].dt.floor("s")  # per-second buckets

    # Pivot → one row = one vector
    # each vector representi plot id w timestamp with a wide presentation maa sensors lkol
    wide = (
        df.pivot_table(
            index=["plot_id", "bucket"],
            columns="sensor_type",
            values="value",
            aggfunc="mean"
        )
        .reset_index()
        .rename(columns={"bucket": "timestamp"})
    )

    # we filter marokhra bel plot id wel features only
    # keep only complete vectors (temperature, humidity, moisture)
    return wide.dropna(subset=FEATURES)


def score_vectors(wide):
    results = {}

    for plot_id in sorted(wide["plot_id"].unique()):
        model_path = os.path.join(
            MODELS_DIR,
            f"isoforest_plot_{plot_id}.joblib"
        )

        if not os.path.exists(model_path):
            continue

        model = joblib.load(model_path)

        # we filter marokhra bel plot id wel features only
        X = (
            wide[wide["plot_id"] == plot_id][FEATURES]
            .astype(float)
        )

        # score taatina array mta all vectors b score mteehom
        # preds taatina 1 (normal) or -1 (anomaly)
        scores = model.decision_function(X)
        preds = model.predict(X)

        # .mean y3ni percentage mta anomalies fel data kolha
        results[int(plot_id)] = {
            "vectors_tested": int(len(X)),
            "anomaly_count": int((preds == -1).sum()),
            "anomaly_rate": float((preds == -1).mean()) if len(X) else 0.0,
            "score_min": float(scores.min()) if len(scores) else None,
            "score_max": float(scores.max()) if len(scores) else None,
            "score_mean": float(scores.mean()) if len(scores) else None,
        }

    return results


def main():
    wide = fetch_vectors()
    if wide.empty:
        print("No data found.")
        return {}

    results = score_vectors(wide)
    import json
    print(json.dumps(results, indent=2))
    return results


if __name__ == "__main__":
    main()
