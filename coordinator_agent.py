from typing import Dict, Any, List
from agent import Agent
from utils.logging_config import setup_logger, log_with_agent_id

logger = setup_logger(__name__)


class CoordinatorAgent(Agent):
    def __init__(self, agent_id: str, message_bus):
        super().__init__(agent_id, message_bus)
        self.task_routes.update({"handle_request": self.handle_request})

    def handle_request(self, sender: str, payload: Dict[str, Any]) -> None:
        log_with_agent_id(
            logger, self.agent_id, logger.INFO, f"Received user request: {payload}"
        )
        for subtask in self.decompose_request(payload):
            self.send_message(
                subtask.get("agent", "research_agent"),
                subtask.get("task", "process_data"),
                subtask.get("payload", {}),
            )

    def decompose_request(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [{"agent": "research_agent", "task": "process_data", "payload": payload}]
