import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

__version__ = "1.2.0"

__all__ = [
    "__version__",
    "logger",
]
