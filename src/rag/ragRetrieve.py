import os
import pandas as pd

# ============================================================
# LangChain RAG Agent with Google Gemini for Bus Data Analysis
# ============================================================

# --- Configuration ---
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
CSV_PATH = "../../data/raw/bus_data.csv"
CHROMA_PERSIST_DIR = "./chroma_db_"

# --- Load and Split Documents ---
from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = CSVLoader(file_path=CSV_PATH, encoding="utf-8")
docs = loader.load()

# Split into manageable chunks for embedding
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = text_splitter.split_documents(docs)
print(f"Loaded {len(docs)} rows, split into {len(chunks)} chunks")

# --- Initialize Gemini Chat Model ---
from langchain_google_genai import ChatGoogleGenerativeAI

"""
# to prepare a langchain dataframe agent, you would run--

```
import os 
import pandas as pd

from IPython.display import Markdown, HTML, display
from langchain.schema import HumanMessage
from langchain_openai import AzureChatOpenAI

model = AzureChatOpenAI(
    azure_deployment="gpt-4-1106",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_version="2024-02-15-preview",
    temperature=0
)

df = pd.read_csv("./data/all-states-history.csv").fillna(value = 0)

from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

agent = create_pandas_dataframe_agent(
    llm=model,
    df=df,
    agent_type=AgentType.OPENAI_FUNCTIONS,  # <-- REQUIRED
    verbose=True
)

agent.invoke("how many rows are there?")

# we could also design our prompt and ask the question--
```
CSV_PROMPT_PREFIX = """
# First set the pandas display options to show all the columns,
# get the column names, then answer the question.
"""

CSV_PROMPT_SUFFIX = """
# - **ALWAYS** before giving the Final Answer, try another method.
# Then reflect on the answers of the two methods you did and ask yourself
# if it answers correctly the original question.
# If you are not sure, try another method.
# - If the methods tried do not give the same result,reflect and
# try again until you have two methods that have the same result.
# - If you still cannot arrive at a consistent result, say that
# you are not sure of the answer.
# - If you are sure of the correct answer, create a beautiful
# and thorough response using Markdown.
# - **DO NOT MAKE UP AN ANSWER OR USE PRIOR KNOWLEDGE,
# ONLY USE THE RESULTS OF THE CALCULATIONS YOU HAVE DONE**.
# - **ALWAYS**, as part of your "Final Answer", explain how you got
# to the answer on a section that starts with: "\n\nExplanation:\n".
# In the explanation, mention the column names that you used to get
# to the final answer.
"""

QUESTION = <i have some sample questions at the bottom of the script>

agent.invoke(CSV_PROMPT_PREFIX + QUESTION + CSV_PROMPT_SUFFIX)

# RAG chains are simpler/stabler
# Agents are good at multi-step math but are less reliable
"""

chat_model = ChatGoogleGenerativeAI(
    google_api_key=GOOGLE_API_KEY,
    model="gemini-2.5-flash",
    temperature=0.2,
)

# --- Initialize Embedding Model (local, no rate limits) ---
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"  # Fast and accurate, runs locally
)

# Store the chunks in vector store
from langchain_community.vectorstores import Chroma

# Embed each chunk and load it into the vector store
db = Chroma.from_documents(chunks, embedding_model, persist_directory=CHROMA_PERSIST_DIR)

# setting a Connection with the ChromaDB
db_connection = Chroma(persist_directory=CHROMA_PERSIST_DIR, embedding_function=embedding_model)

# converting CHROMA db_connection to Retriever Object
retriever = db_connection.as_retriever(search_kwargs={"k": 5})

print(f"Retriever ready: {type(retriever)}")

from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

chat_template = ChatPromptTemplate.from_messages([
    # System Message Prompt Template
    SystemMessage(content="""You are an expert data analyst specializing in bus sensor telemetry data.
                  Given context from a CSV containing acceleration statistics (accel_stats) with 
                  percentile columns (p1, p10, p90, p99) for x, y, and z axes, answer questions 
                  accurately. Provide numerical insights and explain patterns when relevant."""),
    # Human Message Prompt Template
    HumanMessagePromptTemplate.from_template("""Answer the question based on the given context.
    Context: {context}
    Question: {question}
    Answer: """)
])

from langchain_core.output_parsers import StrOutputParser

output_parser = StrOutputParser()

from langchain_core.runnables import RunnablePassthrough

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | chat_template
    | chat_model
    | output_parser
)

# TODO: we can customize the question below
# response = rag_chain.invoke("""Please summarize the csv file""")
response = rag_chain.invoke("""Find outliers where accel_stats_x_p1 and accel_stats_x_p99 are both extreme (possible sensor issues or very rough segments).""")
print("\n--- Response ---")
print(response)

### sample prompts

"""
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
"""

print(response)