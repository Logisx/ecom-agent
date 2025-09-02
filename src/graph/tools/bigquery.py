import json
import logging
import re
from typing import Optional

from google.cloud import bigquery
from langchain_core.tools import tool

from src.config.app_config_loader import AppConfigLoader
from src.services.big_query_runner import BigQueryRunner


_RUNNER: Optional[BigQueryRunner] = None
MAX_BYTES_SCANNED = 1024 * 1024 * 1024  # 1 GB
MAX_LIMIT = 1000


def get_runner() -> BigQueryRunner:
    """
    Return a shared BigQueryRunner instance.
    Uses provided args or falls back to config. Initializes once only.

    Returns:
        BigQueryRunner: The shared BigQueryRunner instance.
    """
    global _RUNNER
    if _RUNNER is not None:
        logging.info("Using existing BigQueryRunner instance.")
        return _RUNNER

    logging.info("Initializing BigQueryRunner instance.")
    config_loader = AppConfigLoader()
    bigquery_config = config_loader.get_config().get("bigquery", {})

    project_id = bigquery_config.get("project_id")
    dataset_id = bigquery_config.get("dataset_id")

    if dataset_id is None or project_id is None:
        logging.error("Missing BigQuery configuration: project_id or dataset_id.")
        raise ValueError("dataset_id must be provided either as an argument or via config")

    _RUNNER = BigQueryRunner(project_id=project_id, dataset_id=dataset_id)
    logging.info("BigQueryRunner initialized successfully.")
    return _RUNNER


@tool
def query_bigquery_tool(*, sql: str, top_n_rows: Optional[int] = 500) -> str:
    """
    Execute a BigQuery Standard SQL statement and return dataframe of top_n_rows (default to 500 rows).

    Args:
        sql (str): The SQL query to execute.
        top_n_rows (Optional[int]): Number of rows to return. Defaults to 500.

    Returns:
        str: Query result as a string or error message.
    """
    logging.info("Received query for execution.")

    # --- SQL Safety Check ---
    if not sql.lstrip().lower().startswith("select"):
        logging.warning("Query rejected: Only SELECT queries are allowed.")
        return "ERROR: Only read-only SQL queries (starting with SELECT) are allowed."

    if re.search(r"select\s+\*\s+from", sql.lower()):
        logging.warning("Query rejected: SELECT * is not allowed.")
        return "ERROR: `SELECT *` is not allowed. Please specify the columns you need."

    limit_match = re.search(r"limit\s+(\d+)", sql.lower())
    if limit_match:
        limit_value = int(limit_match.group(1))
        if limit_value > MAX_LIMIT:
            logging.warning("Query rejected: LIMIT exceeds maximum allowed.")
            return f"ERROR: The LIMIT value of {limit_value} exceeds the maximum allowed limit of {MAX_LIMIT}."
    else:
        logging.warning("Query rejected: Missing LIMIT clause.")
        return "ERROR: Your query must include a numeric LIMIT clause."

    try:
        runner = get_runner()

        # --- Dry run ---
        try:
            logging.info("Performing dry run for query.")
            job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
            dry_run_job = runner.client.query(sql, job_config=job_config)

            if dry_run_job.total_bytes_processed > MAX_BYTES_SCANNED:
                logging.warning("Query exceeds byte scan limit.")
                return f"ERROR: Query would process {dry_run_job.total_bytes_processed} bytes, which exceeds the limit of {MAX_BYTES_SCANNED} bytes."

            logging.info("Dry run successful.")
        except bigquery.GoogleCloudError as e:
            logging.error(f"Dry run failed: {e}")
            return f"Dry run failed: {e}"

        # --- Actual run ---
        logging.info("Executing query.")
        job_config = bigquery.QueryJobConfig(dry_run=False, use_query_cache=True)
        df = runner.execute_query(sql, job_config=job_config)
        logging.info("Query executed successfully.")
        return df.to_string() if top_n_rows is None else df.head(top_n_rows).to_string()

    except Exception as e:
        logging.error(f"Query execution failed: {e}")
        return f"ERROR: {e}"


@tool
def describe_bigquery_table_schema_tool(*, table_name: str) -> str:
    """
    Return JSON schema for a table in the dataset (e.g., orders, users).

    Args:
        table_name (str): The name of the table to describe.

    Returns:
        str: JSON schema of the table or error message.
    """
    logging.info(f"Describing schema for table: {table_name}.")
    try:
        runner = get_runner()
        schema = runner.get_table_schema(table_name)
        logging.info("Schema retrieved successfully.")
        return json.dumps(schema)
    except Exception as e:
        logging.error(f"Failed to retrieve schema: {e}")
        return f"ERROR: {e}"
