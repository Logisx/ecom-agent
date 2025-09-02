import json
import logging
import re
from typing import Optional

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from src.services.big_query_runner import BigQueryRunner
from src.config.app_config_loader import AppConfigLoader

from google.cloud import bigquery

# Global runner instance (lazy init so we only build it once when first needed)
_RUNNER: Optional[BigQueryRunner] = None
MAX_BYTES_SCANNED = 1024 * 1024 * 1024  # 1 GB
MAX_LIMIT = 1000


def get_runner() -> BigQueryRunner:
    """
    Return a shared BigQueryRunner instance.
    Uses provided args or falls back to config. Initializes once only.
    """
    global _RUNNER
    if _RUNNER is not None:
        return _RUNNER

    # Load from yaml config if not provided
    config_loader = AppConfigLoader()
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
    top_n_rows: int | None = 500,
) -> str:
    """Execute a BigQuery Standard SQL statement and return dataframe of top_n_rows (default to 500 rows)."""
    # --- SQL Safety Check ---
    # A simple but effective check to ensure only read-only queries are executed.
    if not sql.lstrip().lower().startswith("select"):
        return "ERROR: Only read-only SQL queries (starting with SELECT) are allowed."

    # Avoid SELECT *
    if re.search(r"select\s+\*\s+from", sql.lower()):
        return "ERROR: `SELECT *` is not allowed. Please specify the columns you need."

    # Enforce a reasonable LIMIT value
    limit_match = re.search(r"limit\s+(\d+)", sql.lower())
    if limit_match:
        limit_value = int(limit_match.group(1))
        if limit_value > MAX_LIMIT:
            return f"ERROR: The LIMIT value of {limit_value} exceeds the maximum allowed limit of {MAX_LIMIT}."
    else:
        return "ERROR: Your query must include a numeric LIMIT clause."


    try:
        runner = get_runner()

        # --- Dry run ---
        try:
            job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
            dry_run_job = runner.client.query(sql, job_config=job_config)
            logging.info("Dry run successful.")

            if dry_run_job.total_bytes_processed > MAX_BYTES_SCANNED:
                return f"ERROR: Query would process {dry_run_job.total_bytes_processed} bytes, which exceeds the limit of {MAX_BYTES_SCANNED} bytes."

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
