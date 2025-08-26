from typing import Dict, Any
from src.services.big_query_runner import BigQueryRunner
import logging

logger = logging.getLogger(__name__)

_runner: BigQueryRunner | None = None

def _get_runner() -> BigQueryRunner:
    global _runner
    if _runner is None:
        _runner = BigQueryRunner()
    return _runner

def node(state: Dict[str, Any]) -> Dict[str, Any]:
    sql = state.get("sql") or ""
    try:
        # emulate dry-run by running with LIMIT and discarding result
        logger.debug("dry_run.node: start", extra={"sql_preview": sql[:120]})
        _ = _get_runner().execute_query(sql)
        state["dry_run_ok"] = True
        state["error"] = None
        logger.info("dry_run.node: ok")
    except Exception as e:
        state["dry_run_ok"] = False
        state["error"] = str(e)
        logger.warning("dry_run.node: failed", extra={"error": state["error"]})
    logger.debug("dry_run.node: end")
    return state
