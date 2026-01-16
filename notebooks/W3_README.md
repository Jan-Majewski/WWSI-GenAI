# W3 - LLM Flows, Agents, and Chat Applications

This directory contains Week 3 materials covering LangChain flows, agents with tools, and chat applications with memory.

## Files Overview

| File | Type | Standalone | Description |
|------|------|------------|-------------|
| `W3-llm-flows-and-monitoring.ipynb` | Notebook | Yes | Sentiment analysis with LLM chain routing |
| `W3-agent_with_tools.py` | Python Script | Yes | Travel booking agent with custom tools |
| `W3_chat_with_memory.py` | Python Script | Yes* | Chatbot backend with conversation memory |
| `W3-chat_app.py` | Streamlit App | No | Web UI for chat (requires backend) |

*Can run standalone for testing, but designed to work with Streamlit frontend.

### BLANK Versions (Exercise Files)
- `W3-llm-flows-and-monitoring copy_BLANK.ipynb` - Exercise version with TODOs
- `W3-agent_with_tools_BLANK.py` - Exercise version with TODOs
- `W3_chat_with_memory_BLANK.py` - Exercise version with TODOs

---

## Prerequisites

### 1. Install Dependencies

```bash
# From project root
pip install -r requirements.txt

# Or install W3-specific packages only
pip install langchain-core langchain-openai langsmith streamlit pandas python-dotenv
```

### 2. Configure Environment Variables

Create a `.env` file in the **project root** (not in `notebooks/`):

```bash
# /Users/.../WWSI-GenAI/.env
OPENAI_API_KEY=sk-your-openai-api-key
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_PROJECT=your-project-name
```

**Important:** The `.env` file must be in the project root. Notebooks load it using `load_dotenv(dotenv_path=Path('..') / '.env')`.

---

## Detailed File Descriptions

### 1. W3-llm-flows-and-monitoring.ipynb

**Purpose:** Demonstrates LangChain flows with conditional routing based on sentiment analysis.

**Content:**
- Sentiment classification using GPT-4o with JSON output parsing
- Positive review handler (generates thank you + voucher offer)
- Negative review handler (generates apology + 25% discount offer)
- `RunnableBranch` for conditional routing based on sentiment
- LangSmith tracing integration for monitoring

**Key Concepts:**
- `JsonOutputParser` for structured LLM outputs
- `PromptTemplate` for creating reusable prompts
- `RunnablePassthrough` and `RunnableBranch` for chain composition
- Conditional execution flow based on LLM output

**Imports (modern LangChain 0.3+):**
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableBranch
```

**How to Run:**
```bash
# Open in Jupyter
jupyter notebook W3-llm-flows-and-monitoring.ipynb

# Or use VS Code / JupyterLab
```

---

### 2. W3-agent_with_tools.py

**Purpose:** Demonstrates a LangChain agent with custom tools for a travel booking system.

**Content:**
- Two custom tools using `@tool` decorator:
  - `save_reservation` - Saves trip reservations to CSV file
  - `read_reservation` - Looks up reservations by ID
- Simple agent loop with tool calling (no AgentExecutor needed)
- Travel booking assistant persona

**Key Concepts:**
- `@tool` decorator for creating custom tools
- `llm.bind_tools()` for tool calling
- `ToolMessage` for returning tool results
- Simple agent loop pattern
- CSV-based data persistence (`reservations.csv`)

**Modern Implementation (LangChain 0.3+):**
```python
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage

@tool
def save_reservation(planned_trip_date: str, trip_destination: str, description: str) -> str:
    """Save a new trip reservation."""
    # ... implementation

tools = [save_reservation, read_reservation]
llm_with_tools = llm.bind_tools(tools)
```

**How to Run:**
```bash
# From project root
python notebooks/W3-agent_with_tools.py
```

**What Happens:**
1. Books a trip to Paris for Dec 25, 2023
2. Queries the reservation status by ID
3. Creates/updates `reservations.csv` in the current working directory

---

### 3. W3_chat_with_memory.py

**Purpose:** Backend chatbot with persistent conversation memory stored in JSON.

**Content:**
- Conversation history management (save/load from JSON)
- Message formatting for LangChain prompts
- `chatbot_response()` function that maintains context across calls
- Unique conversation IDs for multi-session support

**Key Concepts:**
- `ChatPromptTemplate` with `MessagesPlaceholder` for history
- `HumanMessage` and `AIMessage` for conversation formatting
- JSON file-based conversation persistence (`conversation_memory.json`)

**Configuration:**
Uses **OpenAI GPT-4o** by default:
```python
llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o")
```

To use LM Studio (local LLM) instead, uncomment the alternative configuration in the file.

**How to Run (Standalone):**
```bash
python notebooks/W3_chat_with_memory.py
```

**What Happens:**
1. Starts a conversation with "Hi, my name is Alice"
2. Continues with travel planning question
3. Tests memory by asking "What's my name?"

---

### 4. W3-chat_app.py

**Purpose:** Streamlit web interface for the chatbot.

**Requires:** `W3_chat_with_memory.py` (imports `chatbot_response` function)

**Content:**
- Streamlit-based chat UI with styled message bubbles
- Session state management for conversation continuity
- Typing effect animation for AI responses
- "Start New Conversation" button in sidebar

**How to Run:**
```bash
# From notebooks directory
cd notebooks
streamlit run W3-chat_app.py
```

**What Happens:**
1. Opens web browser with chat interface
2. Users can type messages and get AI responses
3. Conversation persists until "Start New Conversation" is clicked

**Requirements:**
- `W3_chat_with_memory.py` must be in the same directory
- OpenAI API key configured in `.env`

---

## Architecture Summary

```
+------------------------+
|   Standalone Files     |
+------------------------+
| W3-llm-flows-and-      |
| monitoring.ipynb       |  (Jupyter Notebook - run cells)
+------------------------+
| W3-agent_with_tools.py |  (python script.py)
+------------------------+

+------------------------+     +------------------------+
|     Frontend (FE)      |     |     Backend (BE)       |
+------------------------+     +------------------------+
|                        |     |                        |
| W3-chat_app.py         |---->| W3_chat_with_memory.py |
| (Streamlit UI)         |     | (LangChain + Memory)   |
|                        |     |                        |
+------------------------+     +------------------------+
                                        |
                                        v
                               +------------------+
                               | conversation_    |
                               | memory.json      |
                               +------------------+
```

---

## Quick Start

### Install and Run

```bash
# 1. Install dependencies (from project root)
pip install -r requirements.txt

# 2. Ensure .env file exists in project root with:
#    OPENAI_API_KEY=sk-your-key
#    LANGSMITH_TRACING=true (optional, for monitoring)

# 3. Run any file
python notebooks/W3-agent_with_tools.py
jupyter notebook notebooks/W3-llm-flows-and-monitoring.ipynb
cd notebooks && streamlit run W3-chat_app.py
```

### Run Each File

| File | Command | Run From |
|------|---------|----------|
| Notebook | `jupyter notebook notebooks/W3-llm-flows-and-monitoring.ipynb` | Project root |
| Agent Script | `python notebooks/W3-agent_with_tools.py` | Project root |
| Chat Backend (test) | `python notebooks/W3_chat_with_memory.py` | Project root |
| Chat Web App | `streamlit run W3-chat_app.py` | `notebooks/` directory |

---

## Generated Files

These files are created during execution:

| File | Created By | Location | Purpose |
|------|------------|----------|---------|
| `reservations.csv` | `W3-agent_with_tools.py` | Current working directory | Stores travel bookings |
| `conversation_memory.json` | `W3_chat_with_memory.py` | Current working directory | Stores chat history |

---

## Troubleshooting

### Import Errors
If you get `ModuleNotFoundError: No module named 'langchain.prompts'` or similar:
```bash
pip install langchain-core langchain-openai
```

**Note:** Modern LangChain (0.3+) uses `langchain_core` for most imports, not `langchain`.

### LangSmith Traces Not Showing
1. Ensure `.env` file is in **project root** (not `notebooks/`)
2. Restart Jupyter kernel after creating/modifying `.env`
3. Verify environment variables load:
   ```python
   import os
   print(os.getenv('LANGSMITH_TRACING'))  # Should print: true
   ```

### Streamlit Not Found
```bash
pip install streamlit
```

---

## Summary Table

| File | Standalone | Run Command | Notes |
|------|------------|-------------|-------|
| `W3-llm-flows-and-monitoring.ipynb` | Yes | Jupyter | Sentiment routing demo |
| `W3-agent_with_tools.py` | Yes | `python` | Travel booking agent |
| `W3_chat_with_memory.py` | Yes | `python` | Backend (can test solo) |
| `W3-chat_app.py` | **No** | `streamlit run` | Needs backend in same dir |
