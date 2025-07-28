# message_bus.py
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
            print(f"[MessageBus] Unknown recipient: {recipient}")

    def broadcast(self, message):
        """Send message to all registered agents except sender"""
        sender = message.get("sender")
        for agent_id, agent in self.agents.items():
            if agent_id != sender:
                msg = message.copy()
                msg["recipient"] = agent_id
                agent.receive_message(msg)
