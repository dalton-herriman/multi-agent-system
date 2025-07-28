# message_bus.py
class MessageBus:
    def __init__(self):
        self.agents = {}

    def register(self, agent):
        self.agents[agent.agent_id] = agent

    def deliver(self, message):
        recipient = message.get("recipient")
        if recipient in self.agents:
            self.agents[recipient].receive_message(message)
        else:
            print(f"[MessageBus] Unknown recipient: {recipient}")

    def broadcast(self, message):
        """Send message to all registered agents"""
        for agent_id in self.agents:
            if agent_id != message.get("sender"):
                message_copy = message.copy()
                message_copy["recipient"] = agent_id
                self.deliver(message_copy)
