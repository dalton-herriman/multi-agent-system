from agent import Agent


class CoordinatorAgent(Agent):
    def __init__(self, agent_id, message_bus):
        super().__init__(agent_id, message_bus)
        self.task_routes.update({"handle_request": self.handle_request})

    def handle_request(self, sender, payload):
        print(f"[{self.agent_id}] Received user request: {payload}")
        subtasks = self.decompose_request(payload)
        for subtask in subtasks:
            agent = subtask.get("agent", "research_agent")
            task = subtask.get("task", "process_data")
            subpayload = subtask.get("payload", {})
            self.send_message(agent, task, subpayload)

    def decompose_request(self, payload):
        """
        Breaks a user request into subtasks.
        Override or extend this method for custom decomposition logic.
        Returns a list of dicts: {"agent": ..., "task": ..., "payload": ...}
        """
        # Default: treat the whole payload as a single process_data task
        return [{"agent": "research_agent", "task": "process_data", "payload": payload}]
