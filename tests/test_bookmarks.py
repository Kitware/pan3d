from pan3d import DatasetBuilder  # noqa: F401


def test_import_bookmark():
    viewer = DatasetBuilder()
    viewer.server.start()
    viewer.import_bookmark("examples/example_bookmark.json")
