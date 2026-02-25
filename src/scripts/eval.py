"""
eval.py
-------
Single script: runs each test query through the Gemini 2.5 pandas dataframe
agent, computes the pandas ground-truth answer, and prints a side-by-side
comparison.

Usage:
    # Run against the original dataset:
    python eval.py

    # Run against the 100x enlarged dataset:
    python eval.py --enlarged

    # Point to any CSV:
    python eval.py --csv path/to/file.csv
"""

import os
import sys
import argparse
import pandas as pd
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

BASE_DIR     = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CSV_DEFAULT  = os.path.join(BASE_DIR, "data", "raw", "bus_data.csv")
CSV_ENLARGED = os.path.join(BASE_DIR, "data", "raw", "bus_data_enlarged.csv")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
LOG_FILE   = os.path.join(OUTPUT_DIR, "eval_responses.md")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ====================================================
# TEST QUERIES
# ====================================================

TEST_QUERIES = [
    "How many rows have accel_mean exactly equal to 9.344?",
    "How many rows have accel_variance greater than 0.15?",
    "Count the data points where accel_stats_z_p99 exceeds 11.0.",
    "What is the maximum value of accel_stats_x_p99 and its corresponding timestamp?",
    "Calculate the average accel_stats_y_p90 across the dataset.",
    "What is the standard deviation of accel_mean?",
    "Count the number of unique latitude-longitude locations.",
    "Find the top 5 most frequent locations by grouping latitude and longitude.",
    "What is the earliest timestamp and its accel_mean value?",
    "How many data points have longitude between -84.39 and -84.38?",
]

# ====================================================
# Ground-truth computations (one per query, same order)
# ====================================================

def gt_accel_mean_exact(df):
    count = (df["accel_mean"] == 9.344).sum()
    return str(count)

def gt_variance_above(df):
    count = (df["accel_variance"] > 0.15).sum()
    return str(count)

def gt_z_p99_above(df):
    count = (df["accel_stats_z_p99"] > 11.0).sum()
    return str(count)

def gt_max_x_p99(df):
    idx = df["accel_stats_x_p99"].idxmax()
    return f"{df.loc[idx, 'accel_stats_x_p99']} at {df.loc[idx, 'timestamp']}"

def gt_avg_y_p90(df):
    return f"{df['accel_stats_y_p90'].mean():.4f}"

def gt_std_accel_mean(df):
    return f"{df['accel_mean'].std():.6f}"

def gt_unique_locations(df):
    count = len(df[["latitude", "longitude"]].drop_duplicates())
    return str(count)

def gt_top5_locations(df):
    top5 = df.groupby(["latitude", "longitude"]).size().nlargest(5).reset_index(name="count")
    return top5.to_string(index=False)

def gt_earliest_timestamp(df):
    row = df.sort_values("timestamp").iloc[0]
    return f"timestamp={row['timestamp']}, accel_mean={row['accel_mean']}"

def gt_lon_range(df):
    count = df[(df["longitude"] >= -84.39) & (df["longitude"] <= -84.38)].shape[0]
    return str(count)

GROUND_TRUTH_FNS = [
    gt_accel_mean_exact,
    gt_variance_above,
    gt_z_p99_above,
    gt_max_x_p99,
    gt_avg_y_p90,
    gt_std_accel_mean,
    gt_unique_locations,
    gt_top5_locations,
    gt_earliest_timestamp,
    gt_lon_range,
]

# ====================================================
# LLM + guardrail setup (runs after df is loaded)
# ====================================================

def build_schema_summary(dataframe):
    """Auto-derive column summary from any dataframe — no hardcoding."""
    lines = []
    for col in dataframe.columns:
        dtype = str(dataframe[col].dtype)
        sample = dataframe[col].dropna().iloc[0] if not dataframe[col].dropna().empty else "N/A"
        lines.append(f"- '{col}' (dtype: {dtype}, e.g. {sample})")
    return "\n".join(lines)


def init_llm_components(df):
    if not GROQ_API_KEY:
        raise ValueError("Missing GROQ_API_KEY. Set it before running eval.py")

    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name="llama-3.1-8b-instant",
        temperature=0.0,
    )

    schema = build_schema_summary(df)
    system_context = f"""
You are the Gatekeeper for a tabular dataset.
The dataset contains ONLY the following {len(df.columns)} columns:
{schema}

YOUR JOB:
1. Analyze the USER QUERY.
2. Determine if this dataset's columns can theoretically answer it.
3. If YES, output exactly "PROCEED".
4. If NO, output a polite explanation citing which data is missing.
"""
    guardrail_chain = (
        ChatPromptTemplate.from_messages([("system", system_context), ("human", "{query}")])
        | llm
        | StrOutputParser()
    )

    col_list     = ", ".join(df.columns)
    sample_rows  = df.head(2).to_dict(orient="records")
    total_rows   = len(df)

    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=False,
        allow_dangerous_code=True,
        agent_type="zero-shot-react-description",
    )

    def ask_agent(user_query):
        """Guardrail → pandas agent → raw answer string."""
        decision = guardrail_chain.invoke({"query": user_query})
        if "PROCEED" not in decision:
            return f"[REJECTED] {decision}"

        prompt = (
            f"Dataset schema — columns: [{col_list}]. "
            f"Sample rows: {sample_rows}. Total rows: {total_rows}.\n"
            f"Question: '{user_query}'\n"
            "Return ONLY the concise answer (a number, value, or short table). "
            "No explanation needed."
        )
        try:
            return agent.invoke(prompt)["output"]
        except Exception as e:
            return f"[ERROR] {e}"

    return ask_agent


# ====================================================
# Logging
# ====================================================

def log_results(results, csv_path):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n# Eval Run [{timestamp}] — {csv_path}\n\n")
        for i, (query, gt, llm_ans) in enumerate(results, 1):
            f.write(f"## Q{i}: {query}\n\n")
            f.write(f"| | Answer |\n|---|---|\n")
            f.write(f"| **Ground Truth** | {gt} |\n")
            f.write(f"| **LLM** | {llm_ans} |\n\n")
            f.write("---\n")
    print(f"\nResults logged → {LOG_FILE}")


# ====================================================
# Main
# ====================================================

def run(csv_path):
    print(f"\nLoading: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Rows: {len(df):,}  Columns: {len(df.columns)}")

    ask_agent = init_llm_components(df)

    results = []
    for i, (query, gt_fn) in enumerate(zip(TEST_QUERIES, GROUND_TRUTH_FNS), 1):
        print(f"\n{'─' * 60}")
        print(f"Q{i}: {query}")
        print(f"{'─' * 60}")

        gt_answer  = gt_fn(df)
        llm_answer = ask_agent(query)

        print(f"  GROUND TRUTH : {gt_answer}")
        print(f"  LLM ANSWER   : {llm_answer}")

        results.append((query, gt_answer, llm_answer))

    log_results(results, csv_path)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run eval: LLM agent vs pandas ground truth.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--enlarged", action="store_true",
                       help="Use the 100x enlarged dataset.")
    group.add_argument("--csv", type=str, default=None,
                       help="Path to a custom CSV file.")
    args = parser.parse_args()

    if args.csv:
        csv_path = args.csv
    elif args.enlarged:
        csv_path = CSV_ENLARGED
    else:
        csv_path = CSV_DEFAULT

    run(csv_path)
