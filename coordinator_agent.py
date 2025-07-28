from agent import Agent


class CoordinatorAgent(Agent):
    def __init__(self, agent_id, message_bus):
        super().__init__(agent_id, message_bus)
        self.task_routes.update({"handle_request": self.handle_request})

    def handle_request(self, sender, payload):
        print(f"[{self.agent_id}] Received user request: {payload}")
        # Example: Break into subtasks
        self.send_message("research_agent", "process_data", payload)
