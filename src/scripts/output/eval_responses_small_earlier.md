
# Eval Run - Original Bus Dataset

Shape: (1219, 17)

## Q1: How many rows have accel_mean exactly equal to 9.344?

| | Answer |
|---|---|
| **Ground Truth** | 59 |
| **LLM** | 59 |

---
## Q2: How many rows have accel_variance greater than 0.15?

| | Answer |
|---|---|
| **Ground Truth** | 588 |
| **LLM** | 588 |

---
## Q3: Count the data points where accel_stats_z_p99 exceeds 11.0.

| | Answer |
|---|---|
| **Ground Truth** | 153 |
| **LLM** | 153 |

---
## Q4: What is the maximum value of accel_stats_x_p99 and its corresponding timestamp?

| | Answer |
|---|---|
| **Ground Truth** | 2.758 at 2025-06-06 16:30:37 |
| **LLM** | 2.758 |

---
## Q5: Calculate the average accel_stats_y_p90 across the dataset.

| | Answer |
|---|---|
| **Ground Truth** | 4.2193 |
| **LLM** | 4.219285479901559 |

---
## Q6: What is the standard deviation of accel_mean?

| | Answer |
|---|---|
| **Ground Truth** | 0.048388 |
| **LLM** | 0.04838827180446493 |

---
## Q7: Count the number of unique latitude-longitude locations.

| | Answer |
|---|---|
| **Ground Truth** | 1218 |
| **LLM** | 1072768 |

---
## Q8: Find the top 5 most frequent locations by grouping latitude and longitude.

| | Answer |
|---|---|
| **Ground Truth** |  latitude  longitude  count
33.773378 -84.399111      2
33.772734 -84.397084      1
33.772763 -84.397208      1
33.772775 -84.396959      1
33.772784 -84.397328      1 |
| **LLM** | latitude  longitude  frequency
329  33.773378 -84.399111          2
0    33.772734 -84.397084          1
810  33.777404 -84.395453          1
816  33.777466 -84.389748          1
815  33.777462 -84.389937          1 |

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
| **Ground Truth** | 243 |
| **LLM** | 243 |

---
