import os
import sys

# =========================================================
# ADD PROJECT ROOT (folder that contains manage.py)
# =========================================================
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
sys.path.insert(0, PROJECT_ROOT)

print("PROJECT_ROOT =", PROJECT_ROOT)
print("Exists manage.py?",
      os.path.exists(os.path.join(PROJECT_ROOT, "manage.py")))
print("Has agriculture_backend folder?",
      os.path.isdir(os.path.join(PROJECT_ROOT, "agriculture_backend")))

# =========================================================
# DJANGO SETTINGS
# =========================================================
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "agriculture_backend.settings"
)

import django
django.setup()

# =========================================================
# IMPORTS
# =========================================================
import pandas as pd
import numpy as np
import joblib

from monitoring.models import SensorReading

# =========================================================
# PATHS & CONSTANTS
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

FEATURES = ["temperature", "humidity", "moisture"]
SOURCE_VALUE = "simulator_scenarios"

# =========================================================
# MAIN LOGIC
# =========================================================
def main():
    print("\n--- Pulling data from DB ---")

    qs = (
        SensorReading.objects
        .filter(source=SOURCE_VALUE)
        .order_by("-timestamp")[:1500]
    )

    print("Readings fetched:", qs.count())

    if not qs.exists():
        print("Error: No data found for source =", SOURCE_VALUE)
        print("Available sources:",
              list(SensorReading.objects.values_list("source", flat=True).distinct()))
        return

    # ORM → DataFrame
    rows = list(
        qs.values("plot_id", "timestamp", "sensor_type", "value")
    )
    df = pd.DataFrame(rows)

    print("Raw DF shape:", df.shape)
    print("Sensor types:", df["sensor_type"].unique())
    print("Plots:", df["plot_id"].unique())

    # =====================================================
    # FIX: Timestamp bucketing (critical)
    # =====================================================
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["bucket"] = df["timestamp"].dt.floor("s")  # per-second buckets

    # =====================================================
    # Pivot → one row = one vector
    # =====================================================
    wide = df.pivot_table(
        index=["plot_id", "bucket"],
        columns="sensor_type",
        values="value",
        aggfunc="mean"
    ).reset_index().rename(columns={"bucket": "timestamp"})

    print("Wide DF before dropna:", wide.shape)
    print("Wide columns:", wide.columns.tolist())

    # Ensure all required features exist
    for f in FEATURES:
        if f not in wide.columns:
            wide[f] = np.nan

    before = len(wide)
    wide = wide.dropna(subset=FEATURES)
    print(f"Wide after dropna: {len(wide)} rows (dropped {before - len(wide)})")

    if wide.empty:
        print("Error: No complete sensor vectors found.")
        print("Reason: sensors not aligned in same second.")
        return

    # =====================================================
    # Load model per plot & score
    # =====================================================
    print("\n--- Scoring with Isolation Forest models ---")

    # Optional: inject synthetic anomalies for testing
    INJECT_TEST_ANOMALIES = True  # Set to False to test real data only
    
    for plot_id in sorted(wide["plot_id"].unique()):
        model_path = os.path.join(
            MODELS_DIR,
            f"isoforest_plot_{plot_id}.joblib"
        )

        if not os.path.exists(model_path):
            print(f"Warning: No model found for plot {plot_id}")
            continue

        model = joblib.load(model_path)

        X = (
            wide[wide["plot_id"] == plot_id][FEATURES]
            .astype(float)
        )
        
        # Get anomaly scores (lower = more anomalous)
        scores = model.decision_function(X)
        preds = model.predict(X)   # 1 = normal, -1 = anomaly
        
        rate = (preds == -1).mean() * 100
        
        print(f"\nPlot {plot_id} Results:")
        print(f"  Vectors tested: {len(X)}")
        print(f"  Anomaly rate: {rate:.2f}%")
        print(f"  Score range: [{scores.min():.3f}, {scores.max():.3f}]")
        print(f"  Score mean: {scores.mean():.3f}")
        
        # Show top 5 most anomalous readings (even if not flagged)
        if len(scores) > 0:
            top_indices = np.argsort(scores)[:5]
            print(f"\n  Top 5 most anomalous readings:")
            for i, idx in enumerate(top_indices, 1):
                row = X.iloc[idx]
                print(f"    {i}. Score={scores[idx]:.3f} | "
                      f"T={row['temperature']:.1f}C, "
                      f"H={row['humidity']:.1f}%, "
                      f"M={row['moisture']:.1f}%")
        
        # TEST: Inject synthetic anomalies to verify model works
        if INJECT_TEST_ANOMALIES:
            print(f"\n  Testing with synthetic anomalies...")
            X_test = X.copy()
            # Create 3 synthetic anomalies
            test_anomalies = pd.DataFrame([
                {"temperature": 50.0, "humidity": 10.0, "moisture": 5.0},   # Extreme heat + dry
                {"temperature": 5.0, "humidity": 95.0, "moisture": 90.0},   # Extreme cold + wet
                {"temperature": 35.0, "humidity": 5.0, "moisture": 0.0},    # Desert-like
            ])
            X_with_anomalies = pd.concat([X_test, test_anomalies], ignore_index=True)
            
            test_preds = model.predict(X_with_anomalies)
            test_scores = model.decision_function(X_with_anomalies)
            
            synthetic_preds = test_preds[-3:]
            synthetic_scores = test_scores[-3:]
            
            detected = (synthetic_preds == -1).sum()
            print(f"    Injected 3 synthetic anomalies")
            print(f"    Detected: {detected}/3")
            print(f"    Scores: {synthetic_scores}")

    print("\nDone scoring.")

# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":
    main()
