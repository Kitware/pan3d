import json
import tempfile
from pathlib import Path
import pytest

from pan3d import DatasetBuilder


def test_import_config():
    builder = DatasetBuilder()
    builder.import_config("examples/example_config_noaa.json")
    # With slicing, data_array has shape (180, 360)
    assert builder.data_array.size == 64800


def test_export_config():
    builder = DatasetBuilder()
    import_path = "examples/example_config_xarray.json"
    builder.import_config(import_path)
    with tempfile.TemporaryDirectory() as temp_dir:
        export_path = Path(temp_dir, "exported.json")
        builder.export_config(export_path)
        with open(import_path) as f:
            imported = json.load(f)
        with open(export_path) as f:
            exported = json.load(f)

        # Disregard ui section
        imported.pop("ui", None)
        exported.pop("ui", None)
        assert imported == exported


def test_setters():
    builder = DatasetBuilder()

    builder.dataset_info = {"source": "xarray", "id": "eraint_uvz"}
    # builder will auto select the following:
    # builder.data_array_name = 'z'
    # builder.x = 'longitude'
    # builder.y = 'latitude'
    builder.z = "level"
    builder.t = "month"
    builder.t_index = 1
    builder.slicing = {"longitude": [0, 90, 2]}

    assert builder.dataset_info == {"source": "xarray", "id": "eraint_uvz"}
    assert builder.dataset is not None
    assert builder.data_array_name == "z"
    assert builder.x == "longitude"
    assert builder.y == "latitude"
    assert builder.z == "level"
    assert builder.t == "month"
    assert builder.t_index == 1


def test_import_error():
    # This will only succeed in an environment where
    # pan3d is installed but pan3d[viewer] is not installed.
    builder = DatasetBuilder()
    with pytest.raises(ImportError):
        builder.viewer
