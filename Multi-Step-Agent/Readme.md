# Advanced AI Research Agent

This project details the construction of a sophisticated, multi-step AI agent designed for conducting research on programming tools and technologies. The agent leverages LangGraph to create a predictable and structured workflow, ensuring consistent and high-quality outputs.

The primary goal is to build a coding research assistant that takes a user query (e.g., "Best Firebase alternatives"), performs a series of research steps, and returns a comprehensive analysis and a final recommendation.

## Features

- **Multi-Step Workflow**: The agent follows a predefined sequence of tasks: searching for information, extracting key entities, scraping web pages for details, and generating a final analysis.
- **Structured Output**: Utilizes Pydantic models to force the LLM to return data in a specific, structured format, making the output reliable and easy to parse.
- **Web Research Capabilities**: Integrates Firecrawl to perform web searches and scrape website content for analysis.
- **Controlled Flow**: Uses LangGraph to define the agent's workflow as a state machine, providing explicit control over the agent's operations, in contrast to simpler agents where the LLM has more autonomy.

## Technologies Used

The project is built using the following technologies:
- **Python**: The core programming language.
- **LangChain & LangGraph**: Frameworks for building complex, stateful AI agents. LangGraph is specifically used to construct the agent's workflow as a graph.
- **Firecrawl**: A service for web scraping, crawling, and searching. The project uses the `firecrawl-py` Python SDK for direct API interaction.
- **OpenAI**: Provides the Large Language Model (LLM) that powers the agent's reasoning and generation capabilities (e.g., GPT-4o mini).
- **Pydantic**: Used for data validation and defining schemas for structured LLM outputs.
- **`python-dotenv`**: Manages environment variables for API keys.
- **`uv`**: A fast Python package manager used for project setup and dependency management.

## Project Structure

The project is organized into a modular structure to separate concerns.

```
advanced-agent/
├── .env                  # Environment variables (API keys)
├── main.py               # Main entry point to run the agent
├── pyproject.toml        # Project dependencies for uv
└── src/
    ├── __init__.py
    ├── firecrawl.py      # Service class for Firecrawl API interactions
    ├── models.py         # Pydantic models for structured data
    ├── prompts.py        # Prompts for different LLM tasks
    └── workflow.py       # LangGraph workflow definition (nodes and edges)
```

## Setup and Installation

### Prerequisites
- Python
- Node.js (required for the simple agent example shown in the first part of the video).
- An account with OpenAI and Firecrawl to obtain API keys.

### Installation Steps
1. **Install `uv`** (if not already installed):
    ```bash
    pip install uv
    ```

2. **Initialize the Project and Install Dependencies**:
    Navigate to the `advanced-agent` directory and use `uv` to set up the environment and install the required packages.
    ```bash
    # Initialize a new virtual environment
    uv init .

    # Add the necessary packages
    uv add firecrawl-py langchain langchain-openai langgraph pydantic python-dotenv
    ```

3. **Configure Environment Variables**:
    Create a file named `.env` in the root of the `advanced-agent` directory. Add your API keys to this file.
    ```env
    OPENAI_API_KEY="your_openai_api_key"
    FIRECRAWL_API_KEY="your_firecrawl_api_key"
    ```

## How to Run

Execute the main script from the `advanced-agent` directory using `uv`:
```bash
uv run python main.py
```
The application will start and prompt you to enter a research query.

## Workflow Explained

The project includes both a **Simple Agent** and a more robust **Advanced Agent**.

### Simple Agent

The initial example builds a basic agent using `langchain-mcp-adapter` to connect to a Firecrawl MCP (Model-Context-Protocol) server. In this setup, the agent is given a set of tools and uses the LLM's reasoning to decide which tool to call and when. This approach is powerful but can be unpredictable.

### Advanced Agent Workflow

The core of the project focuses on building an advanced agent with a controlled, predictable workflow using LangGraph.

1. **State Definition**: A `ResearchState` object is defined using a Pydantic model. This object holds all the data that persists and is modified throughout the workflow, including the user query, search results, extracted tools, and final analysis.

2. **Nodes (Workflow Steps)**: The workflow is composed of several nodes, each representing a specific function or task:
    - **Search**: Takes the initial user query and uses the `FirecrawlService` to search the web for relevant company names and articles.
    - **Tool Extraction**: The LLM processes the search results to extract a structured list of tools or companies. This step uses a Pydantic model to ensure the output is correctly formatted.
    - **Scrape and Analyze**: For each extracted tool, this node scrapes its website using Firecrawl and then passes the content to the LLM for a detailed analysis. This analysis is also structured using a Pydantic model (`CompanyAnalysis`).
    - **Recommendation**: After all tools are analyzed, this final node takes the complete dataset and uses the LLM to generate a final summary and recommendation for the user.

3. **Edges (Control Flow)**: The LangGraph `StateGraph` connects these nodes in a specific sequence, ensuring the agent executes the steps in the correct order: `Search -> Extract Tools -> Scrape/Analyze -> Recommend`. This explicit control is what makes the agent's behavior predictable and reliable.