import json
import logging
from typing import Optional

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from src.services.big_query_runner import BigQueryRunner
from src.config.config_loader import ConfigLoader

from google.cloud import bigquery

# Global runner instance (lazy init so we only build it once when first needed)
_RUNNER: Optional[BigQueryRunner] = None


def get_runner() -> BigQueryRunner:
    """
    Return a shared BigQueryRunner instance.
    Uses provided args or falls back to config. Initializes once only.
    """
    global _RUNNER
    if _RUNNER is not None:
        return _RUNNER

    # Load from yaml config if not provided
    config_loader = ConfigLoader()
    bigquery_config = config_loader.get_config().get("bigquery", {})

    project_id = bigquery_config.get("project_id")
    dataset_id = bigquery_config.get("dataset_id")

    if dataset_id is None or project_id is None:
        raise ValueError("dataset_id must be provided either as an argument or via config")

    _RUNNER = BigQueryRunner(project_id=project_id, dataset_id=dataset_id)
    return _RUNNER


@tool
def query_bigquery_tool(
    *,
    sql: str,
    top_n_rows: int | None = 500
) -> str:
    """Execute a BigQuery Standard SQL statement and return dataframe of top_n_rows (default to 500 rows)."""
    try:
        runner = get_runner()

        # --- Dry run to validate the query ---
        try:
            job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
            runner.execute_query(sql, job_config=job_config)
            logging.info("Dry run successful.")
        except Exception as e:
            logging.error(f"Dry run failed: {e}")
            return f"Dry run failed: {e}"

        # --- Actual run ---
        job_config = bigquery.QueryJobConfig(dry_run=False, use_query_cache=True)
        df = runner.execute_query(sql, job_config=job_config)
        return df.to_string() if top_n_rows is None else df.head(top_n_rows).to_string()
    except Exception as e:
        logging.error(f"bigquery_sql_query failed: {e}")
        return f"ERROR: {e}"


@tool
def describe_bigquery_table_schema_tool(
    *,
    table_name: str
) -> str:
    """Return JSON schema for a table in the dataset (e.g., orders, users)."""
    try:
        runner = get_runner()
        schema = runner.get_table_schema(table_name)
        return json.dumps(schema)
    except Exception as e:
        logging.error(f"bigquery_schema_describe failed: {e}")
        return f"ERROR: {e}"
