# utils.py

import logging
import sys

# Configure a basic logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Set default logging level to INFO

# Create console handler and set level to debug
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)  # Console handler can show DEBUG messages

# Create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Add formatter to ch
ch.setFormatter(formatter)

# Add ch to logger
if not logger.handlers:  # Prevent adding multiple handlers if reloaded
    logger.addHandler(ch)


def log_error(message: str, exception: Exception = None):
    """Logs an error message with optional exception details."""
    if exception:
        logger.error(f"{message}: {exception}", exc_info=True)
    else:
        logger.error(message)


def log_info(message: str):
    """Logs an informational message."""
    logger.info(message)


def log_debug(message: str):
    """Logs a debug message."""
    logger.debug(message)


# Example Usage:
if __name__ == "__main__":
    logger.info("This is an info message.")
    logger.debug(
        "This is a debug message."
    )  # Will be shown because console handler is DEBUG
    logger.warning("This is a warning message.")
    try:
        1 / 0
    except ZeroDivisionError as e:
        log_error("Failed to divide by zero", e)
