from argparse import ArgumentParser, BooleanOptionalAction

from pan3d.explorers.slicer import XArraySlicer


def serve():
    parser = ArgumentParser(
        prog="Pan3D",
        description="Launch the Pan3D GeoTrame App",
    )

    parser.add_argument("--import-state")
    parser.add_argument("--server", action=BooleanOptionalAction)
    parser.add_argument("--debug", action=BooleanOptionalAction)

    """
    The XarraySlicer will be configured using the path specified using 
    the `--import-state` parameter
    """
    viewer = XArraySlicer()
    viewer.start()


if __name__ == "__main__":
    serve()