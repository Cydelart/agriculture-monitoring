import os
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

# ---- paths ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "baseline_plot_specific.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(MODELS_DIR, exist_ok=True)

# ---- columns ----
FEATURES = ["temperature", "humidity", "moisture"]
PLOT_COL = "plot_id"
SOURCE_COL = "source"

def train_one_model(df_plot: pd.DataFrame, plot_id: int):
    X = df_plot[FEATURES].astype(float)

    # contamination = expected anomaly rate when scoring later
    # Keep small because your baseline is normal
    model = IsolationForest(
        n_estimators=200,
        contamination=0.02,
        random_state=42
    )
    model.fit(X)
    return model

def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"CSV not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    # safety checks
    missing = [c for c in [PLOT_COL, SOURCE_COL] + FEATURES if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")

    # train ONLY on synthetic baseline rows
    df = df[df[SOURCE_COL] == "synthetic_baseline"].copy()

    # ensure plot_id is numeric
    df[PLOT_COL] = pd.to_numeric(df[PLOT_COL], errors="coerce")
    df = df.dropna(subset=[PLOT_COL])
    df[PLOT_COL] = df[PLOT_COL].astype(int)

    plots = sorted(df[PLOT_COL].unique().tolist())
    print("Plots found:", plots)

    for plot_id in plots:
        df_plot = df[df[PLOT_COL] == plot_id].copy()

        if len(df_plot) < 50:
            print(f" Plot {plot_id}: only {len(df_plot)} rows → consider generating more.")
            continue

        model = train_one_model(df_plot, plot_id)
        out_path = os.path.join(MODELS_DIR, f"isoforest_plot_{plot_id}.joblib")
        joblib.dump(model, out_path)

        print(f" Trained & saved model for plot {plot_id}: {out_path}  (rows={len(df_plot)})")

    print("\nDone.")

if __name__ == "__main__":
    main()
