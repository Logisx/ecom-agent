# EcomAgent README

Hi!

I decided to focus on building a good scalable codebase with an MVP agent solution instead of experimenting with best prompts/models and agent architectures because I wanted to practice more on creating code structure from scratch.

Below you find overview of the system and setup guidelines.

Quick disclaimer: This is written for an Opsfleet reviewer, so the style is a bit informal. Customer-facing documentation would be different.

# Showcase
Please check a 1min video with a sample question from the "expected agent capabilities" from task description.

It is on my [GoogleDisk here](https://drive.google.com/file/d/1bWz2fSvcefXivFzNq8R5GqsiLxr3LW37/view?usp=sharing)


---

# Overview

## Project structure
```
EcomAgent/
├─ config/
│  └─ app-config.yaml           <- define agent, logger and project/dataset configs
├─ src/
│  ├─ config/
│  │  ├─ app_config_loader.py 
│  │  └─ env_config.py 
│  ├─ graph/
│  │  ├─ nodes/
│  │  │  ├─ analyze.py          <- main agent ReAct node with access to bigquery tools
│  │  │  └─ base_node.py        <- abstract base node (initially i planned to have more nodes, but then opted for simplicity)
│  │  ├─ prompts/
│  │  │  └─ analyze.md
│  │  ├─ tools/
│  │  │  └─ bigquery.py         <- tool functions for getting table schema and querying bigquery
│  │  ├─ build.py               <- function to build a graph workflow
│  │  ├─ runner.py              <- function invokes/streams the graph once
│  │  └─ state.py               <- agent state class
│  ├─ services/
│  │  ├─ big_query_runner.py     
│  │  └─ llm.py                 <- initializes llm according to cofig, get_llm() used in nodes
│  └─ main.py                   <- main entrypoint, answers to "check-bq" and "chat" cli commands
├─ tests/
│  └─ unit-tests.py - WIP
├─ .dockerignore
├─ .env.example
├─ .gitignore
├─ .python-version
├─ Dockerfile
├─ graph.png
├─ pyproject.toml
├─ README.md
└─ requirements.txt
```

## Main Workflow

For clarity, I’ll reference filenames rather than function names:

1. `main.py` starts the chat loop (`chat` CLI command) and calls a function from `runner.py` for each question.
2. `runner.py` initializes the graph with `build.py` (once) and invokes it (streaming in the current implementation).
3. `build.py` sets up the tools and the `analyze.py` node (which gets the LLM from `llm.py`).




## Agent

I started with a simple ReAct agent: a single node calling tools. It’s easier to debug and works well with a powerful LLM.

![Agent architecture](https://raw.githubusercontent.com/Logisx/ecom-agent/main/graph.png)

Later I began a 3-node version:

`data_retrieval -> analysis (with python tool to run scripts) -> summarizing`

Would be great to maybe add a plotting tool too (some insights are only visible on plots).

The workflow worked but had issues with very simple queries (e.g., “hi”), where the summarizing node produced verbose output like “Communication is very important ...”. To handle this, I added shortcuts so nodes can finish early for trivial queries, but it had another bugs so ...

I didn’t fully debug this implementation due to time constraints, but it should work with further refinement.

Work-in-progress version: [v2-architecture branch](https://github.com/Logisx/ecom-agent/tree/v2-architecture).

### Model Choice

* **Main model:** `gemini-2.5-flash` via Google API LangGraph wrapper. Strong SQL generation and analytical capabilities.
* **Fallback model:** `gemini-2.0-flash`.
* Use low temperature for stable SQL generation.

Optionally, `gemini-2.5-pro` for higher quality but higher latency - depends on customer needs.


### Tracing & Observability

* Used **LangSmith** for tracing and dashboarding.
* Supports prompt versioning and experiment tracking.



### Guardrails & Safety

* SQL safety: read-only, limit rows, dry-run queries (saves money).
* Max retries set to prevent excessive charges from lagging queries.



## Fallback Strategies

* Switch to fallback model if the main one fails.
* Retry queries with the error context if a tool fails.
* Respond with a polite error if something catastrophic occurs.

Error handling and logging included.


## Improvements

* Introduce a more complex agent structure with tools like Python scripting and plotting.
* Add async if multiple BigQuery tool calls simultaneously needed. I have observed no more than 5 tool calls simultaneously (schema retrieval), so unnecessary for now.
* Implement evaluation pipeline.
* Add tests (not yet done).
* More fallbacks: e.g., high-level insight from partial tool results if breaks in the middle of execution.
* Caching




---

# Setup
I started doing public docker image, but then realized that it may be faster for you and me to manage it manually as env variables and google auth needs to be set up. 

### 1. Environment
```bash
git clone https://github.com/Logisx/ecom-agent.git
cd yourrepo
cp .env.example .env
pip install -r requirements.txt 
echo "Edit .env with your API keys" # langsmith variables are optional
```

### 2. Google Cloud / BigQuery

* Configure BigQuery access ([docs](https://cloud.google.com/bigquery/docs/reference/libraries#client-libraries-install-python))
* Authenticate your environment:

```bash
gcloud auth application-default login
```
---

## Usage

I used new uv package manager (liked it):
```bash
uv run -m src.main chat 
```

Generic python command:
```bash
python -m src.main chat 
```

Logs displayed in cli:
```bash
python -m src.main chat -v
```

To check BigQuery connectivity
```bash
python -m src.main check-bq 
```