import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

FILES = [
    "baseline_plot_1.csv",
    "baseline_plot_2.csv",
    "baseline_plot_3.csv",
]

OUT = os.path.join(DATA_DIR, "baseline_plot_specific.csv")

REQUIRED = {"timestamp", "plot_id", "temperature", "humidity", "moisture", "source"}

def main():
    frames = []
    for f in FILES:
        path = os.path.join(DATA_DIR, f)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing file: {path}")
        df = pd.read_csv(path)

        missing = REQUIRED - set(df.columns)
        if missing:
            raise ValueError(f"{f} missing columns: {sorted(missing)}")

        frames.append(df)

    merged = pd.concat(frames, ignore_index=True)

    # force correct types
    merged["plot_id"] = pd.to_numeric(merged["plot_id"], errors="coerce").astype("Int64")
    merged = merged.dropna(subset=["plot_id"])
    merged["plot_id"] = merged["plot_id"].astype(int)

    merged.to_csv(OUT, index=False)
    print(f"✅ Saved merged baseline to: {OUT}")
    print("Rows per plot:")
    print(merged["plot_id"].value_counts().sort_index())

if __name__ == "__main__":
    main()
