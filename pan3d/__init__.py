import logging
from .dataset_builder import DatasetBuilder

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

__version__ = "0.8.9"

try:
    from .dataset_viewer import DatasetViewer

    __all__ = [DatasetBuilder, DatasetViewer]
except Exception:
    # Trame is not installed, DatasetViewer will not be accessible
    __all__ = [DatasetBuilder]
