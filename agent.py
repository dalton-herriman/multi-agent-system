import logging

# Create module-specific logger
logger = logging.getLogger(__name__)

# Configure logger only if not already configured
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class Agent:
    def __init__(self, agent_id, message_bus=None, max_context=100):
        self.agent_id = agent_id
        self.context = []
        self.max_context = max_context
        self.message_bus = message_bus
        self.task_routes = self._init_task_routes()

    def _init_task_routes(self):
        return {
            "ping": self.handle_ping,
            "process_data": self.handle_process_data,
        }

    def send_message(self, recipient, task, payload):
        message = {
            "sender": self.agent_id,
            "recipient": recipient,
            "task": task,
            "payload": payload,
        }

        if self.message_bus:
            self.message_bus.deliver(message)
        else:
            logger.error(f"[{self.agent_id}] No message bus available to send message")
            raise RuntimeError(f"No message bus available to send message")

    def receive_message(self, message):
        # Validate message
        if not all(field in message for field in ("sender", "recipient", "task")):
            logger.warning(f"[{self.agent_id}] Invalid message format: {message}")
            return

        if message["recipient"] != self.agent_id:
            logger.warning(
                f"[{self.agent_id}] Message not for this agent: {message['recipient']}"
            )
            return

        # Process message
        if len(self.context) >= self.max_context:
            self.context.pop(0)
        self.context.append(message)

        task = message["task"]
        payload = message.get("payload", {})
        sender = message["sender"]

        logger.info(
            f"[{self.agent_id}] received task '{task}' from {sender} with payload: {payload}"
        )

        handler = self.task_routes.get(task)

        if handler:
            try:
                handler(sender, payload)
            except Exception as e:
                logger.error(f"[{self.agent_id}] Error in task '{task}': {e}")
        else:
            self.handle_unknown_task(task, payload)

    def handle_ping(self, sender, payload):
        if sender == self.agent_id:
            logger.info(f"[{self.agent_id}] Task sent to self, ignoring.")
            return
        self.send_message(sender, "pong", {"status": "alive"})

    def handle_process_data(self, sender, payload):
        self.send_message(
            sender, "data_processed", {"result": self.process_data(payload)}
        )

    def handle_unknown_task(self, task, payload):
        logger.info(f"[{self.agent_id}] Unknown task: {task}")

    def process_data(self, payload):
        if isinstance(payload, (list, tuple, dict)):
            item_count = len(payload)
        else:
            item_count = 0
        return {"summary": f"Processed {item_count} items"}
