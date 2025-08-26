import logging

from src.graph.nodes.base_node import BaseNode
from src.graph.state import AgentState

class PlanSQLNode(BaseNode):
    def __call__(self, state: AgentState) -> AgentState:
        print("plansql node started")

        
        SYSTEM_PROMPT = (
            "You are a data analysis assistant for the thelook_ecommerce dataset. "
            "When asked a question, produce BigQuery Standard SQL that uses fully-qualified, backticked table names, "
            "then summarize key findings in plain English. Focus on actionable insights.\n\n"
            "Tables and columns:\n"
            "- orders(order_id, user_id, status, gender, created_at, returned_at, shipped_at, delivered_at, num_of_item)\n"
            "- order_items(id, order_id, user_id, product_id, inventory_item_id, status, created_at, shipped_at, delivered_at, returned_at, sale_price)\n"
            "- products(id, cost, category, name, brand, retail_price, department, sku, distribution_center_id)\n"
            "- users(id, first_name, last_name, email, age, gender, state, street_address, postal_code, city, country, latitude, longitude, traffic_source, created_at, user_geom)\n"
        )

        dataset_id = state.get("dataset_id", "bigquery-public-data.thelook_ecommerce")  # type: ignore[index]
        question = state.get("question", "")  # type: ignore[index]
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Dataset: {dataset_id}\n"
            "Rules: Use backticked fully-qualified names like `{dataset}.{table}`; only existing column names; Standard SQL.\n"
            "Return ONLY the SQL inside triple backticks.\n\n"
            f"Question: {question}\n"
        )

        msg = self.llm.invoke(prompt)
        text = msg.content if isinstance(msg.content, str) else str(msg.content)
        sql = self._extract_sql_from_text(text)
        logging.debug(f"Planned SQL:\n{sql}")
        state["sql"] = sql  # type: ignore[index]
        print("plansql node finished")
        return state

    @staticmethod
    def _extract_sql_from_text(text: str) -> str:
        """Extract SQL inside triple backticks. Fallback to raw text."""
        if "```" in text:
            parts = text.split("```")
            # Try to pick the first fenced block content
            for i in range(1, len(parts), 2):
                candidate = parts[i].strip()
                # Drop optional language tag like ```sql\n
                first_newline = candidate.find("\n")
                if first_newline != -1 and candidate[:first_newline].lower() in {"sql", "bigquery", "bq"}:
                    return candidate[first_newline + 1 :].strip()
                return candidate
        return text.strip()





