import logging
from .dataset_builder import DatasetBuilder


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

__version__ = "0.9.1"

try:
    from .dataset_viewer import DatasetViewer
    from .explorers.slice_explorer import SliceExplorer

    __all__ = [DatasetBuilder, DatasetViewer, SliceExplorer]
except Exception:
    # Trame is not installed, DatasetViewer will not be accessible
    __all__ = [DatasetBuilder]
