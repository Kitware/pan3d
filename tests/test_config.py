import json
import tempfile
from pathlib import Path

from pan3d import DatasetBuilder  # noqa: F401


def test_import_config():
    viewer = DatasetBuilder()
    viewer.import_config("examples/example_config.json")
    assert viewer.data_array.size == 4622832


def test_export_config():
    viewer = DatasetBuilder()
    import_path = "examples/example_config_2.json"
    viewer.import_config(import_path)
    with tempfile.TemporaryDirectory() as temp_dir:
        export_path = Path(temp_dir, "exported.json")
        viewer.export_config(export_path)
        with open(import_path) as f:
            imported = json.load(f)
        with open(export_path) as f:
            exported = json.load(f)
        assert imported == exported
