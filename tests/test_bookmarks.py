from pan3d import Pan3DViewer  # noqa: F401


def test_import_bookmark():
    viewer = Pan3DViewer()
    viewer.server.start()
    viewer.import_bookmark("examples/example_bookmark.json")
