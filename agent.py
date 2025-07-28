class Agent:
    def __init__(self, agent_id, message_bus=None):
        self.agent_id = agent_id
        self.context = []
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
            print(f"[{self.agent_id}] No message bus available to send message")

    def receive_message(self, message):
        self.context.append(message)

        task = message.get("task")
        payload = message.get("payload", {})
        sender = message.get("sender")

        print(
            f"[{self.agent_id}] received task '{task}' from {sender} with payload: {payload}"
        )
        handler = self.task_routes.get(task)

        if handler:
            handler(sender, payload)
        else:
            self.handle_unknown_task(task, payload)

    def handle_ping(self, sender, payload):
        self.send_message(sender, "pong", {"status": "alive"})

    def handle_process_data(self, sender, payload):
        self.send_message(
            sender, "data_processed", {"result": self.process_data(payload)}
        )

    def handle_unknown_task(self, task, payload):
        print(f"[{self.agent_id}] Unknown task: {task}")

    def process_data(self, payload):
        try:
            item_count = len(payload)
        except TypeError:
            item_count = 0
        return {"summary": f"Processed {item_count} items"}
