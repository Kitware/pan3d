import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

__version__ = "1.1.5"

__all__ = [
    "__version__",
    "logger",
]
