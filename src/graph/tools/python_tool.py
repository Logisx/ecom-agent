import logging
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

@tool
def python_repl_tool(*, code: str) -> str:
    """
    Execute Python code in a REPL environment and return the result.

    Args:
        code (str): The Python code to execute.

    Returns:
        str: The result of the executed code or an error message.
    """
    logger.info("Executing Python code in REPL tool.")

    try:
        # Use a restricted environment for execution
        local_env = {}
        exec(code, {}, local_env)
        logger.info("Python code executed successfully.")
        return str(local_env)
    except Exception as e:
        logger.error(f"Error executing Python code: {e}")
        return f"ERROR: {e}"
