from argparse import ArgumentParser, BooleanOptionalAction
from pan3d.dataset_builder import DatasetBuilder


def serve():
    parser = ArgumentParser(
        prog="Pan3D",
        description="Launch the Pan3D Dataset Viewer",
    )

    parser.add_argument("-C", "--config_path")
    parser.add_argument("-D", "--dataset")
    parser.add_argument("-c", "--catalogs", nargs="+")
    parser.add_argument("-S", "--server", action=BooleanOptionalAction)
    parser.add_argument("-d", "--debug", action=BooleanOptionalAction)

    args = parser.parse_args()

    builder = DatasetBuilder(
        dataset=args.dataset,
        catalogs=args.catalogs,
    )
    if args.config_path:
        builder.import_config(args.config_path)
    builder.viewer.start(debug=args.debug)


if __name__ == "__main__":
    serve()
