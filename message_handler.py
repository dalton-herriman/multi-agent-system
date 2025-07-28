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


class MessageBus:
    def __init__(self):
        self.agents = {}

    def register(self, agent):
        self.agents[agent.agent_id] = agent

    def deliver(self, message):
        recipient = message.get("recipient")
        agent = self.agents.get(recipient)
        if agent:
            agent.receive_message(message)
        else:
            logger.warning(f"[MessageBus] Unknown recipient: {recipient}")

    def broadcast(self, message):
        sender = message.get("sender")
        for agent_id, agent in self.agents.items():
            if agent_id != sender:
                msg = message.copy()
                msg["recipient"] = agent_id
                agent.receive_message(msg)
