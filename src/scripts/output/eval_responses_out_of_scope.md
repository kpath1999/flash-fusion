
# Eval Run [2026-02-25 12:51:58] — /Users/kausar/Documents/flash-fusion/data/raw/bus_data.csv

## Q1: What was the average vehicle speed during high accel_variance?

| | Answer |
|---|---|
| **Ground Truth** | Dataset lacks vehicle speed column and deriving speed via double-integration is not feasible |
| **LLM** | [REJECTED] Average vehicle speed is not directly supported by available columns. |

---
## Q2: At what timestamps did the battery level drop below 20%?

| | Answer |
|---|---|
| **Ground Truth** | Dataset lacks battery level column - cannot track battery status |
| **LLM** | [REJECTED] missing column 'battery_level' |

---
## Q3: How many unique driver IDs are in the dataset?

| | Answer |
|---|---|
| **Ground Truth** | Dataset lacks driver ID column - cannot count unique drivers |
| **LLM** | [REJECTED] missing columns |

---
## Q4: What is the gyroscope mean value for accel_mean = 9.344?

| | Answer |
|---|---|
| **Ground Truth** | Dataset lacks gyroscope data - only has accelerometer statistics |
| **LLM** | [REJECTED] Gyroscope mean value is not available in the provided dataset columns. |

---
## Q5: What was the weather at the location with maximum accel_stats_z_p99?

| | Answer |
|---|---|
| **Ground Truth** | Dataset lacks weather information - cannot correlate with external weather data |
| **LLM** | [REJECTED] Missing columns for weather information. |

---
## Q6: Calculate total distance traveled between consecutive timestamps.

| | Answer |
|---|---|
| **Ground Truth** | Dataset lacks detailed positional tracking - cannot calculate distance between sparse GPS points |
| **LLM** | [REJECTED] Requires external calculation of distance between consecutive points. |

---
## Q7: Did the vehicle stop at any traffic lights based on longitude?

| | Answer |
|---|---|
| **Ground Truth** | Dataset lacks traffic infrastructure data - cannot identify traffic light locations |
| **LLM** | [REJECTED] The query requires information about traffic lights, which is not directly supported by the available columns. |

---
## Q8: How many potholes were hit based on accel_stats_x_p90 spikes?

| | Answer |
|---|---|
| **Ground Truth** | Dataset lacks road condition sensors - cannot detect potholes from acceleration alone |
| **LLM** | [REJECTED] The query requires speculative modeling/derivation not directly supported by available columns. |

---
## Q9: Predict the next latitude from current acceleration trends.

| | Answer |
|---|---|
| **Ground Truth** | Dataset lacks sufficient temporal density - cannot reliably predict future positions |
| **LLM** | [REJECTED] speculative modeling/derivation not directly supported by available columns |

---
## Q10: What is the fuel efficiency during periods of low accel_variance?

| | Answer |
|---|---|
| **Ground Truth** | Dataset lacks engine/fuel consumption data - cannot determine fuel efficiency |
| **LLM** | [REJECTED] Fuel efficiency is not directly supported by available columns. |

---
