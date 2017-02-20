"""Helper to create logger instance."""
from briefy.common.log import LOG_SERVER
from briefy.common.log import logstash

import logging


def create_logger(name:str, tags:list):
    """Create a new logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    cs = logging.StreamHandler()
    cs.setLevel(logging.INFO)

    logger.addHandler(cs)

    if LOG_SERVER:
        log_handler = logstash.LogstashHandler(
            LOG_SERVER, 5543, version=1, tags=tags
        )
        logger.addHandler(log_handler)
    return logger


worker_logger = create_logger(name='briefy.leica.worker', tags=['Worker', 'briefy.leica'])
tasks_logger = create_logger(name='briefy.leica.tasks', tags=['Tasks', 'briefy.leica'])
