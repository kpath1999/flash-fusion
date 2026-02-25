import os
import numpy as np
import pandas as pd

# --- Configuration ---
CSV_PATH = "../../data/raw/bus_data.csv"
OUTPUT_DIR = "./output"
NEWCSV_FILE = os.path.join(OUTPUT_DIR, "bus_data_enlarged.csv")
MULTIPLIER = 100

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. load data
df = pd.read_csv(CSV_PATH)

print("\nDATASET COLUMNS:\n")
print(df.columns)

print(f"\nORIGINAL SHAPE: {df.shape}")
print("\nFIRST FEW ROWS:\n")
print(df.head())

# 2. enlarge the dataset 100x with realistic noise
np.random.seed(42)
enlarged_frames = [df.copy()]  # keep original as-is

for i in range(1, MULTIPLIER):
    copy = df.copy()

    # add small gaussian noise to numeric columns so rows aren't identical
    numeric_cols = copy.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        std = copy[col].std()
        noise_scale = std * 0.02  # 2% of std keeps data realistic
        copy[col] = copy[col] + np.random.normal(0, noise_scale, len(copy))

    # offset timestamps so copies span different time windows
    copy["timestamp"] = pd.to_datetime(copy["timestamp"]) + pd.Timedelta(days=i)
    copy["timestamp"] = copy["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    enlarged_frames.append(copy)

df_enlarged = pd.concat(enlarged_frames, ignore_index=True)

# 3. save
df_enlarged.to_csv(NEWCSV_FILE, index=False)

print(f"\nENLARGED SHAPE: {df_enlarged.shape}")
print(f"Saved to {NEWCSV_FILE}")