"""
verify_answers.py
-----------------
Ground-truth validation for the test queries used in intentRecog.py.
Computes the expected answer for each question using raw pandas, then
(optionally) runs the same questions through the LLM agent and prints
a side-by-side comparison.

Usage:
    # Ground truth only (no API calls):
    python verify_answers.py

    # Full comparison (calls Gemini via intentRecog):
    python verify_answers.py --compare
"""

import os
import sys
import argparse
import pandas as pd

# --- Configuration ---
CSV_PATH = "../../data/raw/bus_data.csv"


# ====================================================
# Ground-truth computations — one function per query
# ====================================================

def gt_accel_mean_above_threshold(df, threshold=9.35):
    """Q1: Which rows have accel_mean greater than <threshold>?"""
    result = df[df["accel_mean"] > threshold]
    return (
        f"Found {len(result)} row(s) with accel_mean > {threshold}.\n"
        f"{result[['timestamp', 'accel_mean']].head(20).to_string(index=False)}"  # show first 20
    )


def gt_max_accel_variance(df):
    """Q2: What is the maximum accel_variance and when did it occur?"""
    idx = df["accel_variance"].idxmax()
    row = df.loc[idx]
    return (
        f"Max accel_variance = {row['accel_variance']} "
        f"at timestamp {row['timestamp']}"
    )


def gt_out_of_scope():
    """Q3: How many passengers were on the bus? (should be rejected)"""
    return "REJECTED — no passenger count column exists in the dataset."


def gt_avg_accel_z_p99(df):
    """Q4: What is the average accel_stats_z_p99 across the entire dataset?"""
    avg = df["accel_stats_z_p99"].mean()
    return f"Average accel_stats_z_p99 = {avg:.4f}"


def gt_coords_max_variance(df):
    """Q5: GPS coordinates for the row with highest accel_variance?"""
    idx = df["accel_variance"].idxmax()
    row = df.loc[idx]
    return (
        f"Latitude = {row['latitude']}, Longitude = {row['longitude']} "
        f"(accel_variance = {row['accel_variance']})"
    )


def gt_count_variance_above(df, threshold=1.0):
    """Q6: How many readings have accel_variance above <threshold>?"""
    count = (df["accel_variance"] > threshold).sum()
    return f"{count} readings with accel_variance > {threshold}"


def gt_timestamps_x_p99_above(df, threshold=2.5):
    """Q7: List timestamps where accel_stats_x_p99 exceeds <threshold>."""
    result = df[df["accel_stats_x_p99"] > threshold]
    return (
        f"{len(result)} timestamp(s) where accel_stats_x_p99 > {threshold}.\n"
        f"{result[['timestamp', 'accel_stats_x_p99']].head(20).to_string(index=False)}"  # show first 20
    )

"""
Revised NL query list:
1) "How many rows have accel_mean exactly equal to 9.344?"
2) "How many rows have accel_variance greater than 0.15?"
3) "Count the data points where accel_stats_z_p99 exceeds 11.0?"
4) "What is the maximum value of accel_stats_x_p99 and its corresponding timestamp?"
5) "Calculate the average accel_stats_y_p90 across the dataset."
6) "What is the standard deviation of accel_mean?"
7) "Count the number of unique latitude-longitude locations.
8) "Find the top 5 most frequent locations by grouping latitude and longitude."
9) "What is the earliest timestamp and its accel_mean value?"
10) "How many data points have longitude between -84.39 and -84.38?"
"""

# Ordered list matching TEST_QUERIES in intentRecog.py
GROUND_TRUTH_FNS = [
    ("Which rows have accel_mean greater than 9.35?",        gt_accel_mean_above_threshold),
    ("What is the maximum accel_variance and when did it occur?", gt_max_accel_variance),
    ("How many passengers were on the bus?",                  gt_out_of_scope),
    ("What is the average accel_stats_z_p99 across the entire dataset?", gt_avg_accel_z_p99),
    ("What are the GPS coordinates for the row with the highest accel_variance?", gt_coords_max_variance),
    ("How many readings have accel_variance above 1.0?",     gt_count_variance_above),
    ("List the timestamps where accel_stats_x_p99 exceeds 2.5.", gt_timestamps_x_p99_above),
]


def print_ground_truth(df):
    """Print pandas ground-truth answers for every test query."""
    print("\n" + "=" * 70)
    print("GROUND-TRUTH ANSWERS (pandas)")
    print("=" * 70)

    results = []
    for i, (query, fn) in enumerate(GROUND_TRUTH_FNS, 1):
        # out-of-scope needs no df
        answer = fn() if fn is gt_out_of_scope else fn(df)
        results.append((query, answer))
        print(f"\n--- Q{i}: {query}")
        print(answer)

    return results


def run_comparison(df):
    """Run queries through the LLM agent and compare side-by-side."""
    # import intentRecog from sibling folder
    intent_dir = os.path.join(os.path.dirname(__file__), "..", "intent")
    sys.path.insert(0, os.path.abspath(intent_dir))

    from intentRecog import process_bus_query  # noqa: E402

    gt_results = print_ground_truth(df)

    print("\n\n" + "=" * 70)
    print("SIDE-BY-SIDE COMPARISON")
    print("=" * 70)

    for i, (query, gt_answer) in enumerate(gt_results, 1):
        print(f"\n{'─' * 60}")
        print(f"Q{i}: {query}")
        print(f"{'─' * 60}")

        print(f"\n  [GROUND TRUTH]\n  {gt_answer}")

        llm_answer = process_bus_query(query)
        # truncate long LLM answers for readability
        display = llm_answer[:500] + "..." if len(llm_answer) > 500 else llm_answer
        print(f"\n  [LLM ANSWER]\n  {display}")


# ====================================================
# Main
# ====================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify intentRecog answers against pandas ground truth.")
    parser.add_argument("--compare", action="store_true",
                        help="Also run queries through the LLM and show side-by-side comparison.")
    parser.add_argument("--csv", type=str, default=CSV_PATH,
                        help="Path to the CSV file to validate against.")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    print(f"Loaded {len(df)} rows from {args.csv}")

    if args.compare:
        run_comparison(df)
    else:
        print_ground_truth(df)
