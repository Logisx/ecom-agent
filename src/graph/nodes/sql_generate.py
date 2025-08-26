from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

DEFAULT_SQL = """
SELECT oi.order_id, p.category, oi.sale_price, oi.created_at
FROM `bigquery-public-data.thelook_ecommerce.order_items` AS oi
JOIN `bigquery-public-data.thelook_ecommerce.products` AS p
  ON oi.product_id = p.id
WHERE oi.created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)
LIMIT 100
"""

def node(state: Dict[str, Any]) -> Dict[str, Any]:
    # For bootstrap, emit a safe default SQL; later replace with LLM-generated
    logger.debug("sql_generate.node: start")
    state["sql"] = DEFAULT_SQL.strip()
    logger.info("sql_generate.node: sql_created", extra={"sql_preview": state["sql"][:120]})
    logger.debug("sql_generate.node: end")
    return state

