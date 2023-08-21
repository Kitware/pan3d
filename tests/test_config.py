from pan3d import DatasetBuilder  # noqa: F401


def test_import_config():
    viewer = DatasetBuilder()
    viewer.import_config("examples/example_config.json")
    assert viewer.data_array.size == 184913280000
