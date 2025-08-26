from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.debug("route.node: start", extra={"message_count": len(state.get("messages", []))})
    # passthrough for now; could classify intent later
    logger.debug("route.node: end")
    return state
