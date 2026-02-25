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

    # when the queries are beyond the scope..
    python eval.py --out_of_scope
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
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.agents import AgentAction, AgentFinish

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

OUT_OF_SCOPE = [
    # missing columns
    "What was the average vehicle speed during high accel_variance?",
    "At what timestamps did the battery level drop below 20%?",
    "How many unique driver IDs are in the dataset?",
    "What is the gyroscope mean value for accel_mean = 9.344?",
    # external data required
    "What was the weather at the location with maximum accel_stats_z_p99?",
    "Calculate total distance traveled between consecutive timestamps.",
    "Did the vehicle stop at any traffic lights based on longitude?",
    # impossible derivations
    "How many potholes were hit based on accel_stats_x_p90 spikes?",
    "Predict the next latitude from current acceleration trends.",
    "What is the fuel efficiency during periods of low accel_variance?",
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

# Ground truth responses for out-of-scope queries - all should indicate insufficient data
GT_OUT_OF_SCOPE = [
    "Dataset lacks vehicle speed column and deriving speed via double-integration is not feasible",
    "Dataset lacks battery level column - cannot track battery status",
    "Dataset lacks driver ID column - cannot count unique drivers",
    "Dataset lacks gyroscope data - only has accelerometer statistics",
    "Dataset lacks weather information - cannot correlate with external weather data",
    "Dataset lacks detailed positional tracking - cannot calculate distance between sparse GPS points",
    "Dataset lacks traffic infrastructure data - cannot identify traffic light locations",
    "Dataset lacks road condition sensors - cannot detect potholes from acceleration alone",
    "Dataset lacks sufficient temporal density - cannot reliably predict future positions",
    "Dataset lacks engine/fuel consumption data - cannot determine fuel efficiency",
]

# ====================================================
# Callback handler to capture agent reasoning trace
# ====================================================

class ThinkingCaptureHandler(BaseCallbackHandler):
    """Collects the agent's Thought / Action / Observation steps into a list."""

    def __init__(self):
        self.steps: list[str] = []

    def on_agent_action(self, action: AgentAction, **kwargs) -> None:
        self.steps.append(f"Thought + Action: {action.log.strip()}")
        self.steps.append(f"Action Input: {action.tool_input}")

    def on_tool_end(self, output: str, **kwargs) -> None:
        self.steps.append(f"Observation: {output.strip()}")

    def on_agent_finish(self, finish: AgentFinish, **kwargs) -> None:
        self.steps.append(f"Final Answer: {finish.return_values.get('output', '').strip()}")

    def get_trace(self) -> str:
        return "\n".join(self.steps) if self.steps else "(no steps captured)"


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

    col_list     = ", ".join(df.columns)
    sample_rows  = df.head(2).to_dict(orient="records")
    total_rows   = len(df)

    """
    i) TODO -- one idea...
    RAG for schema: creating a tiny vector store of column descriptions
    we search for relevant columns first; if none match the query keywords, REJECT
    but i feel build_schema_summary(df) doesn't take all that long anyway

    ii) TODO -- another idea...
    some pre-computation can be done
    the metadata (min, max, unique counts) for every column can be computed during loading
    this metadata would be fed as context
    """

    schema = build_schema_summary(df)
    guardrail_context = f"""
You are a schema gatekeeper for a tabular dataset.

Dataset columns (and dtypes/examples):
{schema}

Decision policy:
1. Return PROCEED only if the query can be answered using ONLY these dataset columns.
2. Return REJECT if the query needs:
   - missing columns,
   - external data sources,
   - speculative modeling/derivation not directly supported by available columns.

Output contract (MUST follow exactly, single line):
- If answerable: PROCEED
- If not answerable: REJECT: <short reason>
"""

    guardrail_chain = (
        ChatPromptTemplate.from_messages(
            [
                ("system", guardrail_context),
                ("human", "Query: {query}"),
            ]
        )
        | llm
        | StrOutputParser()
    )

    # Escape curly braces in sample_rows to prevent LangChain template variable errors
    sample_rows_str = str(sample_rows).replace("{", "{{").replace("}", "}}")
    
    prefix_prompt = (
        f"You are a data analyst. The dataset has columns: {col_list}.\n"
        f"Total rows: {total_rows}.\n\n"
        "TOOL USAGE:\n"
        "- To execute Python: Action: python_repl_ast\n"
        "- Then provide Action Input with valid pandas code\n"
        "- Example: Action Input: df['column'].sum()\n\n"
        "WORKFLOW:\n"
        "1. Think about what calculation is needed\n"
        "2. Execute ONE python_repl_ast action with the necessary pandas code\n"
        "3. Return Final Answer: <result>\n\n"
        "Avoid multiple actions when one suffices. Be direct and concise.\n"
    )

    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,  # disable verbose to reduce I/O overhead
        allow_dangerous_code=True,
        agent_type="zero-shot-react-description",
        prefix=prefix_prompt,
        max_iterations=3,  # reduce from 5 to 3 for faster execution
        agent_executor_kwargs={
            "handle_parsing_errors": True,
        },
    )

    def ask_agent(user_query):
        decision = guardrail_chain.invoke({"query": user_query}).strip()
        if decision != "PROCEED":
            if decision.startswith("REJECT:"):
                reason = decision.split("REJECT:", 1)[1].strip()
                return f"[REJECTED] {reason}", f"Guardrail decision: {decision}"
            return f"[REJECTED] {decision}", f"Guardrail decision: {decision}"

        # Pass query directly - schema already in prefix_prompt, no need to repeat
        handler = ThinkingCaptureHandler()
        try:
            # NAIVE: relies on the LLM to blindly write correct Pandas syntax
            # not understanding the stat distribution or indexing of the data beforehand
            # treats the dataset as a black box until code execution
            # q: say my query said 'accl variance' instead of the proper col name; robust to it?
            result = agent.invoke(user_query, config={"callbacks": [handler]})
            return result["output"], handler.get_trace()
        except Exception as e:
            return f"[ERROR] {e}", handler.get_trace()

    # TODO - q: why does the llm take so long; latency is high; reducing it could be flash-fusion's contribution
    # think about it...this is our naive baseline (RAG, SQL, VocalDB)
    # IDEA: based on the query, the data is organized in a specific manner and then fed to the pandas agent
    # TODO - log the latencies for each query
    return ask_agent

# ====================================================
# Logging
# ====================================================

def log_results(results, csv_path):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n# Eval Run [{timestamp}] — {csv_path}\n\n")
        for i, (query, gt, llm_ans, thinking) in enumerate(results, 1):
            f.write(f"## Q{i}: {query}\n\n")
            f.write(f"| | Answer |\n|---|---|\n")
            f.write(f"| **Ground Truth** | {gt} |\n")
            f.write(f"| **LLM** | {llm_ans} |\n\n")
            f.write(f"**Agent Reasoning:**\n```\n{thinking}\n```\n\n")
            f.write("---\n")
    print(f"\nResults logged → {LOG_FILE}")


# ====================================================
# Main
# ====================================================

def run(csv_path, out_of_scope=False):
    print(f"\nLoading: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Rows: {len(df):,}  Columns: {len(df.columns)}")
    
    # Store out_of_scope flag for use in the evaluation loop
    run.out_of_scope = out_of_scope

    ask_agent = init_llm_components(df)

    results = []

    # Select queries and ground truth based on evaluation mode
    if run.out_of_scope:
        queries = OUT_OF_SCOPE
        ground_truths = GT_OUT_OF_SCOPE
        print("\n🔍 Evaluating OUT-OF-SCOPE queries (should be rejected)...")
    else:
        queries = TEST_QUERIES
        ground_truths = [gt_fn(df) for gt_fn in GROUND_TRUTH_FNS]
        print("\n📊 Evaluating STANDARD queries...")

    for i, (query, gt_answer) in enumerate(zip(queries, ground_truths), 1):
        print(f"\n{'─' * 60}")
        print(f"Q{i}: {query}")
        print(f"{'─' * 60}")

        llm_answer, thinking = ask_agent(query)

        print(f"  GROUND TRUTH : {gt_answer}")
        print(f"  LLM ANSWER   : {llm_answer}")

        results.append((query, gt_answer, llm_answer, thinking))

    log_results(results, csv_path)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run eval: LLM agent vs pandas ground truth.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--enlarged", action="store_true",
                       help="Use the 100x enlarged dataset.")
    group.add_argument("--csv", type=str, default=None,
                       help="Path to a custom CSV file.")
    
    group.add_argument("--out_of_scope", action="store_true",
                       help="Evaluate out-of-scope queries that should be rejected.")
    
    args = parser.parse_args()

    if args.csv:
        csv_path = args.csv
    elif args.enlarged:
        csv_path = CSV_ENLARGED
    else:
        csv_path = CSV_DEFAULT

    run(csv_path, out_of_scope=getattr(args, 'out_of_scope', False))
