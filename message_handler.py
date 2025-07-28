from utils.logging_config import setup_logger

logger = setup_logger(__name__)


class MessageBus:
    def __init__(self):
        self.agents = {}

    def register(self, agent):
        self.agents[agent.agent_id] = agent

    def deliver(self, message):
        if agent := self.agents.get(message.get("recipient")):
            agent.receive_message(message)
        else:
            logger.warning(f"Unknown recipient: {message.get('recipient')}")

    def broadcast(self, message):
        sender = message.get("sender")
        for agent_id, agent in self.agents.items():
            if agent_id != sender:
                agent.receive_message({**message, "recipient": agent_id})
