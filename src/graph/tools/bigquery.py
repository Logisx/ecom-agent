import json
import logging
from typing import Optional

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from src.services.big_query_runner import BigQueryRunner
from src.config.config_loader import ConfigLoader

# Global runner instance (lazy init so we only build it once when first needed)
_RUNNER: Optional[BigQueryRunner] = None


def get_runner(
    project_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    config: Optional[RunnableConfig] = None,
) -> BigQueryRunner:
    """
    Return a shared BigQueryRunner instance.
    Uses provided args or falls back to config. Initializes once only.
    """
    global _RUNNER
    if _RUNNER is not None:
        return _RUNNER

    # Load from yaml config if not provided
    config_loader = ConfigLoader()
    bigquery_config = config_loader.config.get("bigquery", {})

    project_id = project_id or bigquery_config.get("project_id")
    dataset_id = dataset_id or bigquery_config.get("dataset_id")

    # Fallback to values provided via Runnable config's configurable block
    configurable = (config or {}).get("configurable", {}) if isinstance(config, dict) else {}
    project_id = project_id or configurable.get("project_id")
    dataset_id = dataset_id or configurable.get("dataset_id")

    if dataset_id is None:
        raise ValueError("dataset_id must be provided either as an argument or via config")

    _RUNNER = BigQueryRunner(project_id=project_id, dataset_id=dataset_id)
    return _RUNNER


@tool
def query_bigquery_tool(
    *,
    project_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    sql: str,
    top_n_rows: int | None = None,
    config: Optional[RunnableConfig] = None,
) -> str:
    """Execute a BigQuery Standard SQL statement and return dataframe of top_n_rows (all rows if top_n_rows not specified)."""
    try:
        runner = get_runner(project_id, dataset_id, config)
        df = runner.execute_query(sql)
        return df.to_string() if top_n_rows is None else df.head(top_n_rows)
    except Exception as e:
        logging.error(f"bigquery_sql_query failed: {e}")
        return f"ERROR: {e}"


@tool
def describe_bigquery_table_schema_tool(
    *,
    project_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    table_name: str,
    config: Optional[RunnableConfig] = None,
) -> str:
    """Return JSON schema for a table in the dataset (e.g., orders, users)."""
    try:
        runner = get_runner(project_id, dataset_id, config)
        schema = runner.get_table_schema(table_name)
        return json.dumps(schema)
    except Exception as e:
        logging.error(f"bigquery_schema_describe failed: {e}")
        return f"ERROR: {e}"
