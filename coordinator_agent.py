from agent import Agent
import logging

logger = logging.getLogger(__name__)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class CoordinatorAgent(Agent):
    def __init__(self, agent_id, message_bus):
        super().__init__(agent_id, message_bus)
        self.task_routes.update({"handle_request": self.handle_request})

    def handle_request(self, sender, payload):
        logger.info(f"[{self.agent_id}] Received user request: {payload}")
        subtasks = self.decompose_request(payload)
        for subtask in subtasks:
            agent = subtask.get("agent", "research_agent")
            task = subtask.get("task", "process_data")
            subpayload = subtask.get("payload", {})
            self.send_message(agent, task, subpayload)

    def decompose_request(self, payload):
        return [{"agent": "research_agent", "task": "process_data", "payload": payload}]
