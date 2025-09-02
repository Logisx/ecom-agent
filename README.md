A custom LangGraph-based agent that analyzes e-commerce data from Google BigQuery and generates insights.  


---

## Setup

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


```bash
python -m src.main chat -v
```
