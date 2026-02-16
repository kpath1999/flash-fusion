# Flash-Fusion: - Enabling Expressive, Low-Latency Queries on IoT Sensor Streams with LLMs

**[Dashboard](https://sting-sense-map.vercel.app/)** | **[GitHub Repository](https://github.com/kpath1999/sting-sense-map)**

---

## Sample prompts

I can pass these through a RAG engine/vector database and see if it retrieves the relevant rows.

* What is the overall distribution of the x-axis acceleration percentiles (p1, p10, p90, p99)?

* Which axis (x, y, or z) shows the highest 99th percentile values on average?

* What are the minimum, median, and maximum values for each percentile column across the dataset?

* How often do the 99th percentile values exceed a chosen threshold (e.g., 2 g) on each axis?

* Which axis has the most skewed distribution, comparing p1, p10, p90, and p99?

* How do the 99th percentile values on each axis change over time during a single trip?

* During which time windows do we see spikes in accel_stats_y_p99 compared to accel_stats_x_p99 and accel_stats_z_p99?

* Can you compute hourly averages of accel_stats_x_p90 and show which hours are roughest?

* Identify periods where accel_stats_z_p99 stays unusually high for more than N consecutive samples.

* Compare the early part vs. late part of the trip: does accel_stats_x_p99 increase as the trip progresses?

* When accel_stats_x_p99 is high, what are the typical values of accel_stats_y_p99 and accel_stats_z_p99?

* Are there strong correlations between x, y, and z 99th percentile accelerations?

* Are high accel_stats_y_p90 events usually accompanied by high accel_stats_z_p90, or do they occur independently?

* Cluster records based on (accel_stats_x_p90, accel_stats_y_p90, accel_stats_z_p90) and describe the clusters.

* Find segments where one axis is calm (low p99) while another axis is extreme (high p99).

* Find the top 1% most extreme events based on a combined score of x, y, and z 99th percentiles.

* Detect bursts where accel_stats_x_p99 exceeds some threshold at least 3 times in a rolling window.

* Identify “transition points” where accel_stats_z_p90 suddenly jumps compared to the previous window.

* Mark periods that look like heavy braking or sharp turns, based on patterns in x and y percentiles.

* Find outliers where accel_stats_x_p1 and accel_stats_x_p99 are both extreme (possible sensor issues or very rough segments).

* Split the data into equal-length segments and compare average accel_stats_z_p99 in each segment.

* For each segment, compute the ratio between high-end and low-end values, e.g., accel_stats_x_p99 / |accel_stats_x_p1|, and find segments with the largest ratios.

* Identify segments with consistently low accel_stats_y_p90 across all samples (smooth lateral motion).

* Rank segments by “roughness” using a custom metric that combines all three axes’ p90/p99 values.

* Group data by “intensity level” bins (low, medium, high based on p99) and report how much time is spent in each level.

* Compute summary statistics (mean, std, kurtosis) for each percentile column and highlight which columns are most heavy-tailed.

* Fit a simple model to predict accel_stats_z_p99 from the other percentile features; which inputs are most important?

* Perform PCA on all percentile columns; how many components explain most of the variability?

* Compare the variability (standard deviation) of accel_stats_x_p10 vs accel_stats_x_p90; which side of the distribution is more volatile?

* Build a composite “comfort score” from all percentile values and find the worst and best-scoring samples.

* Are there any obvious anomalies, such as accel_stats_x_p1 being greater than accel_stats_x_p90 in some rows?

* How many rows have identical values across multiple percentiles (e.g., p1 = p10 = p90 = p99)?

* Do the percentile values for each axis behave monotonically (p1 ≤ p10 ≤ p90 ≤ p99) across the dataset?

* Are there suspicious constant plateaus in any of the percentile columns, suggesting sensor saturation?

* Compare the distribution of accel_stats_z_p1 and accel_stats_z_p99 to see if the range is realistic.