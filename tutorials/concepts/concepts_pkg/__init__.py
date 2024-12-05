import logging

from concepts_pkg.config import logging_config

# Configure logger for use in package
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging_config.get_console_handler())
logger.propagate = False
