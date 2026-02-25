
# Eval Run - Enlarged Bus Dataset

Shape: (121900, 17)

## Q1: How many rows have accel_mean exactly equal to 9.344?

| | Answer |
|---|---|
| **Ground Truth** | 59 |
| **LLM** | 59 |

---
## Q2: How many rows have accel_variance greater than 0.15?

| | Answer |
|---|---|
| **Ground Truth** | 58438 |
| **LLM** | 58438 |

---
## Q3: Count the data points where accel_stats_z_p99 exceeds 11.0.

| | Answer |
|---|---|
| **Ground Truth** | 14928 |
| **LLM** | 14928 |

---
## Q4: What is the maximum value of accel_stats_x_p99 and its corresponding timestamp?

| | Answer |
|---|---|
| **Ground Truth** | 2.7912980182909743 at 2025-09-05 16:28:55 |
| **LLM** | timestamp            2025-09-05 16:28:55
accel_stats_x_p99               2.791298
Name: 111049, dtype: object |

---
## Q5: Calculate the average accel_stats_y_p90 across the dataset.

| | Answer |
|---|---|
| **Ground Truth** | 4.2192 |
| **LLM** | 4.2192322021513515 |

---
## Q6: What is the standard deviation of accel_mean?

| | Answer |
|---|---|
| **Ground Truth** | 0.048374 |
| **LLM** | 0.04837415658189008 |

---
## Q7: Count the number of unique latitude-longitude locations.

| | Answer |
|---|---|
| **Ground Truth** | 121899 |
| **LLM** | 14815268923 |

---
## Q8: Find the top 5 most frequent locations by grouping latitude and longitude.

| | Answer |
|---|---|
| **Ground Truth** |  latitude  longitude  count
33.773378 -84.399111      2
33.772635 -84.397138      1
33.772641 -84.397243      1
33.772649 -84.397343      1
33.772651 -84.397450      1 |
| **LLM** | |   latitude  |   longitude  |   frequency |
|------------:|--------------:|-------------:|
|  33.773378 |  -84.399111   |           2 |
|  33.772635 |  -84.397138   |           1 |
|  33.777417 |  -84.395477   |           1 |
|  33.777418 |  -84.39601    |           1 |
|  33.777418 |  -84.402665   |           1 | |

---
## Q9: What is the earliest timestamp and its accel_mean value?

| | Answer |
|---|---|
| **Ground Truth** | timestamp=2025-06-06 11:08:35, accel_mean=9.269 |
| **LLM** | 9.269 |

---
## Q10: How many data points have longitude between -84.39 and -84.38?

| | Answer |
|---|---|
| **Ground Truth** | 24323 |
| **LLM** | 24323 |

---
