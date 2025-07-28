import logging
from utils.logging_config import setup_logger, log_with_agent_id

logger = setup_logger(__name__)

class Agent:
    def __init__(self, agent_id, message_bus=None, max_context=100):
        self.agent_id = agent_id
        self.context = []
        self._max_context = max_context
        self.message_bus = message_bus
        self.task_routes = {"ping": self.handle_ping, "process_data": self.handle_process_data}

    def send_message(self, recipient, task, payload):
        if not self.message_bus:
            raise RuntimeError("No message bus available to send message")
        self.message_bus.deliver({"sender": self.agent_id, "recipient": recipient, "task": task, "payload": payload})

    def receive_message(self, message):
        if not all(field in message for field in ("sender", "recipient", "task")):
            log_with_agent_id(logger, self.agent_id, logging.WARNING, f"Invalid message format: {message}")
            return
        if message["recipient"] != self.agent_id:
            log_with_agent_id(logger, self.agent_id, logging.WARNING, f"Message not for this agent: {message['recipient']}")
            return

        self.context.append(message)
        if len(self.context) > self._max_context:
            self.context = self.context[-self._max_context:]
        
        task, payload, sender = message["task"], message.get("payload", {}), message["sender"]
        log_with_agent_id(logger, self.agent_id, logging.INFO, f"received task '{task}' from {sender} with payload: {payload}")

        if handler := self.task_routes.get(task):
            try:
                handler(sender, payload)
            except Exception as e:
                error_type = "Invalid data" if isinstance(e, (ValueError, TypeError)) else "Error"
                log_with_agent_id(logger, self.agent_id, logging.ERROR, f"{error_type} in task '{task}': {e}")
        else:
            self.handle_unknown_task(task, payload)

    def handle_ping(self, sender, payload):
        if sender == self.agent_id:
            log_with_agent_id(logger, self.agent_id, logging.INFO, "Task sent to self, ignoring.")
            return
        self.send_message(sender, "pong", {"status": "alive"})

    def handle_process_data(self, sender, payload):
        self.send_message(sender, "data_processed", {"result": self.process_data(payload)})

    def handle_unknown_task(self, task, payload):
        log_with_agent_id(logger, self.agent_id, logging.INFO, f"Unknown task: {task}")

    def process_data(self, payload):
        item_count = len(payload) if isinstance(payload, (list, tuple, dict)) else 0
        return {"summary": f"Processed {item_count} items"}
