import os
import sys

# =========================================================
# 1) ADD PROJECT ROOT (folder that contains manage.py)
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
# 2) DJANGO SETTINGS
# =========================================================
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "agriculture_backend.settings"
)

import django
django.setup()

# =========================================================
# 3) IMPORTS
# =========================================================
import pandas as pd
import numpy as np
import joblib

from monitoring.models import SensorReading

# =========================================================
# 4) PATHS & CONSTANTS
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

FEATURES = ["temperature", "humidity", "moisture"]
SOURCE_VALUE = "simulator"   # ← EXACT value from your DB

# =========================================================
# 5) MAIN LOGIC
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
        print("❌ No data found for source =", SOURCE_VALUE)
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
        print("❌ No complete sensor vectors found.")
        print("Reason: sensors not aligned in same second.")
        return

    # =====================================================
    # Load model per plot & score
    # =====================================================
    print("\n--- Scoring with Isolation Forest models ---")

    for plot_id in sorted(wide["plot_id"].unique()):
        model_path = os.path.join(
            MODELS_DIR,
            f"isoforest_plot_{plot_id}.joblib"
        )

        if not os.path.exists(model_path):
            print(f"⚠️ No model for plot {plot_id}")
            continue

        model = joblib.load(model_path)

        X = (
            wide[wide["plot_id"] == plot_id][FEATURES]
            .astype(float)
        )

        preds = model.predict(X)   # 1 = normal, -1 = anomaly
        rate = (preds == -1).mean() * 100

        print(
            f"Plot {plot_id}: "
            f"anomaly rate = {rate:.2f}% "
            f"(vectors={len(X)})"
        )

    print("\n✅ Done scoring.")

# =========================================================
# 6) ENTRY POINT
# =========================================================
if __name__ == "__main__":
    main()
