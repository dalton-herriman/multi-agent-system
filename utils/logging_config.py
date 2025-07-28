import logging


def setup_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger


def log_with_agent_id(logger, agent_id, level, message):
    logger.log(level, f"[{agent_id}] {message}")
