from typing import Dict, Any
import logging
import os

logger = logging.getLogger(__name__)


from src.graph.nodes.base_node import BaseNode
from src.graph.state import AgentState

def _load_prompt(template_name: str) -> str:
    import importlib.resources as pkg_resources
    from pathlib import Path
    try:
        from src.graph import prompts as prompts_pkg
        with pkg_resources.files(prompts_pkg).joinpath(template_name).open("r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        here = Path(__file__).resolve().parents[1] / "prompts" / template_name
        return here.read_text(encoding="utf-8")


class SummarizeNode(BaseNode):
    def __call__(self, state: AgentState) -> AgentState:
        logger.info("SummarizeNode called")

        # Find the last tool output in the messages
        last_message = state["messages"][-1]
        preview = ""
        if hasattr(last_message, 'content'):
             # content from a ToolMessage is often a string representation of the data
             preview = str(last_message.content)

        question = state.get("question", "")
        prompt_template = _load_prompt("summarize.md")
        prompt = (
            prompt_template
            .replace("{question}", question)
            .replace("{preview}", preview)
        )
        msg = self.llm.invoke(prompt)
        
        # Return the final summary in the 'summary' field
        return {"summary": msg.content if isinstance(msg.content, str) else str(msg.content)}
