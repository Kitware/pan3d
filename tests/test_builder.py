import json
from pathlib import Path

from pan3d.xarray.algorithm import vtkXArrayRectilinearSource

ROOT_PATH = Path(__file__).parent.parent.resolve()


def read_config(path):
    return json.loads((ROOT_PATH / path).read_text())


def test_import_config():
    conf = read_config("examples/example_config_noaa.json")
    builder = vtkXArrayRectilinearSource()
    builder.load(conf)

    # check available arrays
    assert set(builder.available_arrays) == set(
        ["sea_ice_fraction", "analysed_sst", "mask", "analysis_error"]
    )

    # check array size based on slicing
    builder.arrays = ["mask"]
    ds = builder()
    assert ds.point_data["mask"].size == 10000


def test_export_config():
    conf = read_config("examples/example_config_xarray.json")
    builder = vtkXArrayRectilinearSource()
    builder.load(conf)
    input_conf = conf.get("dataset_config")
    output_conf = builder.state.get("dataset_config")
    input_conf["arrays"] = set(input_conf["arrays"])
    output_conf["arrays"] = set(output_conf["arrays"])
    assert input_conf == output_conf


def test_setters():
    builder = vtkXArrayRectilinearSource()

    builder.load({"data_origin": {"source": "xarray", "id": "eraint_uvz"}})
    builder.t_index = 1

    assert builder.x == "longitude"
    assert builder.y == "latitude"
    assert builder.z == "level"
    assert builder.t == "month"
    assert builder.t_index == 1
