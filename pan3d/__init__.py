import os
import logging

os.environ["TRAME_DISABLE_V3_WARNING"] = "1"

from .viewer import Pan3DViewer  # noqa: E402

logging.getLogger("trame.app").disabled = True

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

__all__ = [Pan3DViewer]
