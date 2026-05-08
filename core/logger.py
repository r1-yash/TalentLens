import logging
from core.config import settings

def get_logger(name: str):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        # Convert string log level from config to actual logging level
        level = getattr(logging, settings.log_level.upper(), logging.INFO)
        logger.setLevel(level)
    return logger
