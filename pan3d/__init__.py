import os
import logging

os.environ["TRAME_DISABLE_V3_WARNING"] = "1"

from .viewer import DatasetBuilder  # noqa: E402

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

__all__ = [DatasetBuilder]
