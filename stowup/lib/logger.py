import logging

LOGGER_NAME = 'stowup'

logger = logging.getLogger(LOGGER_NAME)


def log(level: int, msg: str, **kwargs):
    logger.log(level, msg, **kwargs)
