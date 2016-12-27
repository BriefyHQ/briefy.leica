"""Scripts to import data from knack."""
from briefy.leica import logger

import logging

"""Setup logger to DEBUG mode and to print messages to console."""
ch = logging.StreamHandler()
logger.addHandler(ch)
logger.setLevel(logging.INFO)
