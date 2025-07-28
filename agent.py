from typing import Dict, Any, List, Optional, Callable
from utils.logging_config import setup_logger, log_with_agent_id

logger = setup_logger(__name__)


class Agent:
    def __init__(self, agent_id: str, message_bus=None, max_context: int = 100):
        self.agent_id = agent_id
        self.context: List[Dict[str, Any]] = []
        self.max_context = max_context
        self.message_bus = message_bus
        self.task_routes = self._init_task_routes()

    def _init_task_routes(self) -> Dict[str, Callable]:
        return {
            "ping": self.handle_ping,
            "process_data": self.handle_process_data,
        }

    def send_message(self, recipient: str, task: str, payload: Dict[str, Any]) -> None:
        message = {
            "sender": self.agent_id,
            "recipient": recipient,
            "task": task,
            "payload": payload,
        }

        if not self.message_bus:
            raise RuntimeError("No message bus available to send message")

        self.message_bus.deliver(message)

    def receive_message(self, message: Dict[str, Any]) -> None:
        required_fields = ("sender", "recipient", "task")
        if not all(field in message for field in required_fields):
            log_with_agent_id(
                logger,
                self.agent_id,
                logger.WARNING,
                f"Invalid message format: {message}",
            )
            return

        if message["recipient"] != self.agent_id:
            log_with_agent_id(
                logger,
                self.agent_id,
                logger.WARNING,
                f"Message not for this agent: {message['recipient']}",
            )
            return

        # Efficient context management
        if len(self.context) >= self.max_context:
            self.context.pop(0)
        self.context.append(message)

        task, payload, sender = (
            message["task"],
            message.get("payload", {}),
            message["sender"],
        )
        log_with_agent_id(
            logger,
            self.agent_id,
            logger.INFO,
            f"received task '{task}' from {sender} with payload: {payload}",
        )

        if handler := self.task_routes.get(task):
            try:
                handler(sender, payload)
            except (ValueError, TypeError) as e:
                log_with_agent_id(
                    logger,
                    self.agent_id,
                    logger.ERROR,
                    f"Invalid data in task '{task}': {e}",
                )
            except Exception as e:
                log_with_agent_id(
                    logger, self.agent_id, logger.ERROR, f"Error in task '{task}': {e}"
                )
        else:
            self.handle_unknown_task(task, payload)

    def handle_ping(self, sender: str, payload: Dict[str, Any]) -> None:
        if sender == self.agent_id:
            log_with_agent_id(
                logger, self.agent_id, logger.INFO, "Task sent to self, ignoring."
            )
            return
        self.send_message(sender, "pong", {"status": "alive"})

    def handle_process_data(self, sender: str, payload: Dict[str, Any]) -> None:
        self.send_message(
            sender, "data_processed", {"result": self.process_data(payload)}
        )

    def handle_unknown_task(self, task: str, payload: Dict[str, Any]) -> None:
        log_with_agent_id(logger, self.agent_id, logger.INFO, f"Unknown task: {task}")

    def process_data(self, payload: Dict[str, Any]) -> Dict[str, str]:
        item_count = len(payload) if isinstance(payload, (list, tuple, dict)) else 0
        return {"summary": f"Processed {item_count} items"}
