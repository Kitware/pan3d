from pan3d import DatasetBuilder  # noqa: F401


def test_import_config():
    viewer = DatasetBuilder()
    viewer.server.start()
    viewer.import_config("examples/example_config.json")
