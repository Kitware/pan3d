from argparse import ArgumentParser, BooleanOptionalAction

from pan3d import DatasetBuilder
from pan3d import SliceExplorer

def serve():
    parser = ArgumentParser(
        prog="Pan3D",
        description="Launch the Pan3D GeoTrame App",
    )

    parser.add_argument("--config_path")
    parser.add_argument("--server", action=BooleanOptionalAction)
    parser.add_argument("--debug", action=BooleanOptionalAction)
    args = parser.parse_args()

    builder = DatasetBuilder()
    builder.import_config(args.config_path)

    viewer = SliceExplorer(builder)
    viewer.start()

if __name__ == "__main__":
    serve()
