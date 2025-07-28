import logging
from agent import Agent
from utils.logging_config import setup_logger, log_with_agent_id

logger = setup_logger(__name__)

class CoordinatorAgent(Agent):
    def __init__(self, agent_id, message_bus):
        super().__init__(agent_id, message_bus)
        self.task_routes["handle_request"] = self.handle_request

    def handle_request(self, sender, payload):
        log_with_agent_id(logger, self.agent_id, logging.INFO, f"Received user request: {payload}")
        for subtask in self.decompose_request(payload):
            self.send_message(subtask["agent"], subtask["task"], subtask["payload"])

    def decompose_request(self, payload):
        return [{"agent": "research_agent", "task": "process_data", "payload": payload}]
