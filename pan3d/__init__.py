import logging
from pan3d.dataset_builder import DatasetBuilder
from contextlib import suppress


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

__version__ = "0.9.2"

__all__ = ["DatasetBuilder"]

with suppress(ImportError):
    from pan3d.dataset_viewer import DatasetViewer  # noqa

    __all__.append("DatasetViewer")


with suppress(ImportError):
    from pan3d.explorers.slice_explorer import SliceExplorer  # noqa

    __all__.append("SliceExplorer")
