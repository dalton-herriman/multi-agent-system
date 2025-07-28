import json

class Agent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.context = []

    def send_message(self, recipient, task, payload):
        message = {
            "sender": self.agent_id,
            "recipient": recipient,
            "task": task,
            "payload": payload
        }
        pass
    
    def message_handler(self, message):
        pass
    