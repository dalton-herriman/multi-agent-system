from typing import Dict, Any
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


class MessageBus:
    def __init__(self):
        self.agents: Dict[str, Any] = {}

    def register(self, agent) -> None:
        self.agents[agent.agent_id] = agent

    def deliver(self, message: Dict[str, Any]) -> None:
        recipient = message.get("recipient")
        if agent := self.agents.get(recipient):
            agent.receive_message(message)
        else:
            logger.warning(f"Unknown recipient: {recipient}")

    def broadcast(self, message: Dict[str, Any]) -> None:
        sender = message.get("sender")
        for agent_id, agent in self.agents.items():
            if agent_id != sender:
                agent.receive_message({**message, "recipient": agent_id})
