import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

__version__ = "0.11.2"

__all__ = [
    "logger",
    "__version__",
]
