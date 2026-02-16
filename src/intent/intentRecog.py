## to be continued..
# making the RAG script generalizable and have it handle impossibele questions
# should provide quant -> qual answers (multi-layered)
# moving beyond retrieve and answer

import os
import pandas as pd
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent
# from langchain.agents.agent_types import AgentType
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults

# --- Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CSV_PATH = "../../data/raw/bus_data.csv"
OUTPUT_DIR = "./output"
LOG_FILE = os.path.join(OUTPUT_DIR, "query_responses.md")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. load data
df = pd.read_csv(CSV_PATH)

# 2. initialize models
llm = ChatGoogleGenerativeAI(
    google_api_key=GOOGLE_API_KEY,
    model="gemini-2.5-flash",
    temperature=0.2,
)

# 3. the hallucination guardrail
# TODO: tbh the bullet points are hardcoded and hurt generalizability
system_context = f"""
You are the Gatekeeper for a Bus Sensor Dataset.
The dataset contains ONLY these columns: {list(df.columns)}.
- 'timestamp': Time of recording.
- 'latitude', 'longitude': GPS coordinates.
- 'accel_mean', 'accel_variance': General acceleration stats.
- 'accel_stats_x/y/z_p1/p10/p90/p99': Percentiles of acceleration forces on X (lateral), Y (longitudinal), Z (vertical) axes.

YOUR JOB:
1. Analyze the USER QUERY.
2. Determine if this dataset can theoretically answer it.
3. If YES, output "PROCEED".
4. If NO, output a polite explanation of why, referencing the specific missing data (e.g., "We do not have visual sensors or passenger count data").
"""

guardrail_prompt = ChatPromptTemplate.from_messages([
    ("system", system_context),
    ("human", "{query}")
])

guardrail_chain = guardrail_prompt | llm | StrOutputParser()

# 4. the analysis agent
# replaces standard RAG for CSVs; writing python code to query the data
pandas_agent = create_pandas_dataframe_agent(
    llm,
    df,
    verbose=True,
    allow_dangerous_code=True,
    agent_type='zero-shot-react-description',
    handle_parsing_errors=True
)

# 5. web search with tavily; convert lat/lon coords to landmarks
web_search_tool = TavilySearchResults(max_results=1)

# 5.5 logging function
def log_response(query, response, status="success"):
    """
    Log the query and response to a markdown file with timestamp.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n## Query [{timestamp}]\n\n")
        f.write(f"**User Query:** {query}\n\n")
        f.write(f"**Status:** {status}\n\n")
        f.write(f"**Response:**\n\n{response}\n\n")
        f.write("---\n")
    
    print(f"✅ Response logged to {LOG_FILE}")

# 6. master workflow function
def process_bus_query(user_query):
    print(f"\n--- processing: '{user_query}' ---")

    # a) the guardrail check
    decision = guardrail_chain.invoke({"query": user_query})

    if "PROCEED" not in decision:
        rejection_msg = f"😵‍💫 unable to answer: {decision}"
        log_response(user_query, rejection_msg, status="rejected")
        return rejection_msg
    
    print("Query validated! Proceeding to analysis...")

    # b) analytical translation
    analysis_prompt = (
        f"The user asks: '{user_query}'. "
        "Using the dataframe, perform the necessary aggregation or filtering."
        "Return the relevant data."
    )
    # TODO(high-signal-analysis-prompt): Build this via intent-specific template +
    # structured slots (dataset schema, relevant columns, metrics, aggregation rules,
    # output format) instead of a generic instruction string.

    try:
        insight = pandas_agent.invoke(analysis_prompt)['output']
    except Exception as e:
        error_msg = f"Data analysis error: {e}"
        log_response(user_query, error_msg, status="error")
        return error_msg
    
    print(f"Insight found! {insight}")

    # c) contextual enrichment
    enrichment_context = ""
    if "latitude" in insight.lower() or "longitude" in insight.lower():
         # Ask LLM to extract coordinates for search
        coord_extraction = llm.invoke(f"Extract just the latitude and longitude from this text as a string 'lat, lon': {insight}")
        coords = coord_extraction.content.strip()

        print(f"reverse geocoding coords: {coords}")
        try:
            search_result = web_search_tool.invoke(f"What landmark is at coordinates {coords}?")
            enrichment_context = f"Location context: {search_result}"
        except:
            enrichment_context = "Location context: Could not retrieve external landmark data"
    
    # d) final synthesis; combining into one
    final_prompt = f"""
    User question: {user_query}

    Technical findings (data):
    {insight}

    Context:
    {enrichment_context}

    Task: Synthesize a friendly, helpful answer. Start with a direct answer to the qualitative question, 
    then back it up with the data (mentioning specific values), and mention the landmark if known.
    """

    response = llm.invoke(final_prompt)
    final_response = response.content
    
    # Log the successful response
    log_response(user_query, final_response, status="success")
    
    return final_response


# ==========================================
# TEST CASES
# ==========================================

# 1. Valid Qualitative Question
print(process_bus_query("Where is the ride the roughest?"))

# 2. Invalid Question (Out of scope)
print(process_bus_query("Were the cars nearby flying?"))

# 3. Valid Specific Question
print(process_bus_query("At what time was the highest lateral acceleration (x-axis) recorded?"))