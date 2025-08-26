import logging
from src.graph.nodes.base_node import BaseNode
from src.graph.state import AgentState
from src.services.big_query_runner import BigQueryRunner


class RunSQLNode(BaseNode):
    def __call__(self, state: AgentState) -> AgentState:
        project_id = state.get("project_id")  # type: ignore[index]
        dataset_id = state.get("dataset_id")  # type: ignore[index]
        runner = BigQueryRunner(project_id=project_id, dataset_id=dataset_id)
        try:
            sql = state.get("sql")  # type: ignore[index]
            assert sql, "No SQL to execute"
            df = runner.execute_query(sql)
        except Exception as e:
            logging.error(f"Query failed: {e}")
            fallback_sql = (
                f"SELECT status, COUNT(*) AS num_orders\n"
                f"FROM `{dataset_id}.orders`\n"
                f"GROUP BY status ORDER BY num_orders DESC LIMIT 5"
            )
            logging.info("Running fallback query")
            df = runner.execute_query(fallback_sql)
        state["df_preview"] = df.head(10)  # type: ignore[index]
        return state
