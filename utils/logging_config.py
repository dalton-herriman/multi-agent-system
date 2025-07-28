import logging
from typing import Optional


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Setup logger with consistent formatting."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(level)

    return logger


def log_with_agent_id(
    logger: logging.Logger, agent_id: str, level: int, message: str
) -> None:
    """Log message with agent ID prefix."""
    logger.log(level, f"[{agent_id}] {message}")
